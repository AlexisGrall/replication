from update_google import get_credentials, get_service, get_cal_id, update_google_cal

from get_ade import ade_modif

def main():
    credentials = get_credentials()
    service = get_service(credentials)
    cal_id = get_cal_id(service)
    modifs = ade_modif()
    update_google_cal(cal_id, service, modifs)


if __name__ == "__main__":
    main()
