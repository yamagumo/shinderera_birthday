import birthday_notifier
import time

idols = birthday_notifier.load_idols()
selected = birthday_notifier.load_settings() or []
print('selected:', selected)
for idol in idols:
    if idol["name"] in selected:
        days = birthday_notifier.days_until_birthday(idol["birthday"]) 
        age = idol["age"]
        print(f"notify: {idol['name']} - {days} days")
        birthday_notifier.show_notification(idol["name"], days, age)
        time.sleep(2)
print('done')
