import re
from base64 import b64encode
from io import BytesIO
from pathlib import Path

import olefile


def read_oft_property(ole, property_id):
    """Read a common MAPI string property from an Outlook OLE file."""
    for data_type in ("001F", "001E", "001A"):
        stream_name = f"__substg1.0_{property_id}{data_type}"
        if ole.exists(stream_name):
            raw = ole.openstream(stream_name).read()
            if data_type == "001F":
                return raw.decode("utf-16-le", errors="replace").rstrip("\x00")
            return raw.decode("utf-8", errors="replace").rstrip("\x00")
    return ""


def read_oft_body_html(ole):
    """Read the HTML body property stored by Outlook."""
    for data_type in ("0102", "001F", "001E", "001A"):
        stream_name = f"__substg1.0_1013{data_type}"
        if ole.exists(stream_name):
            raw = ole.openstream(stream_name).read()
            if data_type == "0102":
                for encoding in ("utf-8", "utf-16-le", "cp1252"):
                    try:
                        decoded = raw.decode(encoding)
                        if "<" in decoded or "html" in decoded.lower():
                            return decoded.rstrip("\x00")
                    except UnicodeDecodeError:
                        continue
                return raw.decode("utf-8", errors="replace").rstrip("\x00")
            if data_type == "001F":
                return raw.decode("utf-16-le", errors="replace").rstrip("\x00")
            return raw.decode("cp1252", errors="replace").rstrip("\x00")
    return ""


def read_oft_stream(ole, directory, stream_name):
    """Read a stream from an Outlook attachment storage directory."""
    full_path = list(directory) + [stream_name]
    if not ole.exists(full_path):
        return b""
    return ole.openstream(full_path).read()


def read_oft_attachment_property(ole, directory, property_id):
    """Read a string attachment property from an OFT storage directory."""
    for data_type, encoding in (
        ("001F", "utf-16-le"),
        ("001E", "cp1252"),
        ("001A", "cp1252"),
    ):
        raw = read_oft_stream(ole, directory, f"__substg1.0_{property_id}{data_type}")
        if raw:
            return raw.decode(encoding, errors="replace").rstrip("\x00")
    return ""


def read_oft_attachment_binary(ole, directory):
    """Read the binary payload of an Outlook attachment."""
    for stream_parts in ole.listdir(streams=True, storages=False):
        stream_path = tuple(stream_parts)
        if tuple(stream_path[:-1]) != tuple(directory):
            continue
        stream_name = stream_path[-1].lower()
        if stream_name.endswith("37010102"):
            return ole.openstream(stream_path).read()
    return b""


def embed_oft_inline_images(ole, body_html):
    """Replace cid image references with embedded data URLs from OFT attachments."""
    if not body_html or "cid:" not in body_html:
        return body_html

    cid_data = {}
    image_data = []
    for directory_parts in ole.listdir(storages=True, streams=False):
        directory = tuple(directory_parts)
        if not any(part.lower().startswith("__attach") for part in directory):
            continue
        content_id = read_oft_attachment_property(ole, directory, "3712")
        content_location = read_oft_attachment_property(ole, directory, "3713")
        attachment_data = read_oft_attachment_binary(ole, directory)
        mime_type = (
            read_oft_attachment_property(ole, directory, "370e")
            or "application/octet-stream"
        )
        if attachment_data and mime_type.lower().startswith("image/"):
            data_url = (
                f"data:{mime_type};base64,{b64encode(attachment_data).decode('ascii')}"
            )
            image_data.append((len(attachment_data), data_url))
        if content_id and attachment_data:
            normalized_id = content_id.strip().strip("<>")
            data_url = (
                f"data:{mime_type};base64,{b64encode(attachment_data).decode('ascii')}"
            )
            cid_data[normalized_id.lower()] = data_url
            if content_location:
                cid_data[content_location.strip().lower()] = data_url

    largest_image = max(image_data, default=(0, ""), key=lambda item: item[0])[1]

    def replace_cid(match):
        content_id = match.group(1).strip().strip("<>").lower()
        data_url = cid_data.get(content_id, "")
        if data_url.startswith("data:image/"):
            encoded_payload = data_url.split(",", 1)[-1]
            if len(encoded_payload) <= 256 and largest_image:
                data_url = largest_image
        return data_url or match.group(0)

    return re.sub(r"cid:([^\"'\s>]+)", replace_cid, body_html, flags=re.IGNORECASE)


def parse_oft_file(file_storage):
    """Extract subject, HTML and plain text from an Outlook .oft file."""
    file_bytes = file_storage.read()
    if not file_bytes:
        raise ValueError("Die Outlookvorlage ist leer.")

    try:
        ole = olefile.OleFileIO(BytesIO(file_bytes))
    except (OSError, ValueError, olefile.olefile.OleFileError) as error:
        raise ValueError("Die Datei ist keine gültige Outlookvorlage.") from error

    with ole:
        subject = read_oft_property(ole, "0037")
        body_text = read_oft_property(ole, "1000")
        body_html = read_oft_body_html(ole)
        body_html = embed_oft_inline_images(ole, body_html)

    name = Path(file_storage.filename or "Vorlage.oft").stem
    return {
        "name": name,
        "subject": subject or name,
        "body_html": body_html,
        "body_text": body_text if not body_html else "",
        "active": True,
    }
