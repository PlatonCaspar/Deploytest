# in this document the HTTP Messages are defined

def lookup(e):
    e = e.code
    return msg[str(e)] or msg["default"]

msg = {
    "400": "The server cannot or will not process the request due to an apparent client error (e.g., malformed request syntax, size too large, invalid request message framing, or deceptive request routing).",
    "404": "The requested resource could not be found but may be available in the future. Subsequent requests by the client are permissible.",
    "405": "A request method is not supported for the requested resource; for example, a GET request on a form that requires data to be presented via POST, or a PUT request on a read-only resource.",
    "500": "The Server could not execute your Order. Please Try again. If this error keeps occuring please contact <a href='mailto:stefan.steinmueller@siemens.com'>me</a> and provide some details of what you were doing.",
    "default": "The message For this error is not implemented yet, please contact <a href='mailto:stefan.steinmueller@siemens.com'>me</a> and provide some details of what you were doing."

}