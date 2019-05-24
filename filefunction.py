#------------------가능한 확장자----------------------
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

#--------------------파일형식------------

def allowed_file(filename) :
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS