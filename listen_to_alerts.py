from multiprocessing import Process

from red_alerts_listener.backend.helper_functions import get_red_alert_notification_listener


def start_polling():
    notification_listener = get_red_alert_notification_listener()
    notification_listener.poll_alerts()
    p = Process(target=notification_listener.poll_alerts)
    p.start()


if __name__ == '__main__':
    start_polling()
