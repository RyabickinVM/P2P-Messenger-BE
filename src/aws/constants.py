KB = 1024
MB = 1024 * KB

# all
SUPPORTED_FILE_TYPES_FORM_APPLICATION = {
    'image/png': 'png',
    'image/jpg': 'jpg',
    'image/gif': 'gif',
    'image/jpeg': 'jpeg',
    'image/webp': 'webp',

    'video/mp4': 'mp4',
    'video/webm': 'webm',
    'video/avi': 'avi',
    'video/mov': 'mov',

    'audio/mpeg': 'mp3',
    'audio/x-wav': 'wav',

    'application/pdf': 'pdf',
    'application/msword': 'doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/vnd.ms-powerpoint': 'ppt',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
    'application/vnd.ms-excel': 'xls',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
}

# images types
SUPPORTED_FILE_TYPES_FORM_IMAGE = {
    key: value for key, value in SUPPORTED_FILE_TYPES_FORM_APPLICATION.items() if 'image' in key
}

# videos types
SUPPORTED_FILE_TYPES_FORM_VIDEO = {
    key: value for key, value in SUPPORTED_FILE_TYPES_FORM_APPLICATION.items() if 'video' in key
}

# audio types
SUPPORTED_FILE_TYPES_FORM_AUDIO = {
    key: value for key, value in SUPPORTED_FILE_TYPES_FORM_APPLICATION.items() if 'audio' in key
}

# docs types
SUPPORTED_FILE_TYPES_FROM_DOC = {
    key: value for key, value in SUPPORTED_FILE_TYPES_FORM_APPLICATION.items() if 'application' in key
}
