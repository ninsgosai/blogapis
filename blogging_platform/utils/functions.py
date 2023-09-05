
def custom_response(status, message="Success.", data=None, status_code=200):
    if data is None:
        res = {"status": status, "message": message, "data": "", "status_code": status_code}
    else:
        res = {"status": status, "message": message, "data": data, "status_code": status_code}
    return res