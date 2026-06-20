from enum import Enum


class ResultCodes(Enum):
    SUCCESS = 0
    UNKNOWN_ERROR = -1
    USER_ALREADY_REGISTERED = -2
    USER_NOT_FOUND = -3
    WRONG_VERIFICATION_CODE = -4
    INVALID_CREDENTIALS = -5
    USER_ROLE_NOT_FOUND = -19
    USER_IS_NOT_VERIFIED = -20
    OTP_EXPIRED = -21
    USER_WITH_THIS_PHONE_NUMBER_ALREADY_EXISTS = -22
    OTP_INCORRECT = -59
    INVALID_RESET_TOKEN = -60
    OTP_ALREADY_SENT = -61
    ERROR_SMS_SERVICE = -62
    OTP_HOURLY_LIMIT_REACHED = -63
    OTP_DAILY_LIMIT_REACHED = -64
    NO_CODE_PROVIDED = -65
    FAILED_TO_OBTAIN_TOKEN = -66
    INTERNAL_SERVER_ERROR = -10

ResultMessages = {
    "USER_IS_NOT_VERIFIED": {
        "uz": "User vefikatsiyadan o'tmaga",
        "ru": "User ne verifitsirovan",
        "en": "User is not verified"
    },
    "INTERNAL_SERVER_ERROR": {
        "uz": "Ichki server xatosi!",
        "en": "Internal server error!",
        "ru": "Произошла ошибка. Пожалуйста, попробуйте позже!"
    },
    "UNKNOWN_ERROR": {
        "uz": "Noma'lum xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko‘ring!",
        "en": "An unknown error occurred. Please try again later!",
        "ru": "Произошла неизвестная ошибка. Пожалуйста, попробуйте позже!"
    },
    "USER_ALREADY_REGISTERED": {
        "uz": "Foydalanuvchi allaqachon ro‘yxatdan o‘tgan!",
        "en": "User is already registered!",
        "ru": "Пользователь уже зарегистрирован!"
    },
    "USER_NOT_FOUND": {
        "uz": "Foydalanuvchi topilmadi!",
        "en": "User not found!",
        "ru": "Пользователь не найден!"
    },
    "USER_WITH_THIS_PHONE_NUMBER_ALREADY_EXISTS": {
        "uz": "Foydalanuvchi ushbu telefon raqami bilan allaqachon mavjud!",
        "en": "User with this phone number already exists!",
        "ru": "Пользователь с этим номером телефона уже существует!"
    },
    "WRONG_VERIFICATION_CODE": {
        "uz": "Tasdiqlash kodi noto‘g‘ri!",
        "en": "Wrong verification code!",
        "ru": "Неверный код подтверждения!"
    },
    "INVALID_CREDENTIALS": {
        "uz": "Login yoki parol noto‘g‘ri!",
        "en": "Invalid credentials!",
        "ru": "Неверный логин или пароль!"
    },
    "USER_ROLE_NOT_FOUND": {
        "uz": "Foydalanuvchi  topilmadi!",
        "en": "User  not found!",
        "ru": "пользователя не найдена!"
    },
    "OTP_EXPIRED": {
        "uz": "OTP muddati tugagan!",
        "en": "OTP has expired!",
        "ru": "Срок действия OTP истёк!"
    },
    "OTP_INCORRECT": {
        "uz": "Noto‘g‘ri OTP kiritildi!",
        "en": "Incorrect OTP!",
        "ru": "Неверный OTP!"
    },
    "INVALID_RESET_TOKEN": {
        "uz": "INVALID_RESET_TOKEN",
        "en": "INVALID_RESET_TOKEN",
        "ru": "INVALID_RESET_TOKEN"
    },
    "OTP_ALREADY_SENT": {
        "uz": "OTP allaqachon yuborilgan! Iltimos, biroz kuting va qayta urinib ko‘ring.",
        "en": "OTP has already been sent! Please wait a moment and try again.",
        "ru": "OTP уже был отправлен! Пожалуйста, подождите немного и попробуйте снова."
    },
    "ERROR_SMS_SERVICE": {
        "uz": "SMS xizmatida xatolik yuz berdi!",
        "en": "Error in SMS service!",
        "ru": "Ошибка в SMS сервисе!"
    },
    "OTP_HOURLY_LIMIT_REACHED": {
        "uz": "Soatlik OTP limitiga yetdingiz (5 ta).",
        "en": "Hourly OTP limit reached (5).",
        "ru": "Достигнут почасовой лимит OTP (5)."
    },
    "OTP_DAILY_LIMIT_REACHED": {
        "uz": "Kunlik OTP limitiga yetdingiz (10 ta).",
        "en": "Daily OTP limit reached (10).",
        "ru": "Достигнут дневной лимит OTP (10)."
    },
    "NO_CODE_PROVIDED": {
        "uz": "Google authorization code topilmadi.",
        "en": "Google authorization code was not provided.",
        "ru": "Код авторизации Google не был передан."
    },
    "FAILED_TO_OBTAIN_TOKEN": {
        "uz": "Google token olib bo'lmadi.",
        "en": "Failed to obtain Google token.",
        "ru": "Не удалось получить токен Google."
    }
}
