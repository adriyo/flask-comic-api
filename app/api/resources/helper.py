from datetime import datetime

def parse_published_date(published_date):
    try:
        if '-' in published_date:
            return datetime.strptime(published_date, "%Y-%m-%d").date()
        return datetime.strptime(published_date, "%d/%m/%Y").date()
    except ValueError as e:
        return None