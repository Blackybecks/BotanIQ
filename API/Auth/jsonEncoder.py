import decimal
import datetime
import flask.json

class MyJSONEncoder(flask.json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        if isinstance(obj, datetime.date):
        	return obj.strftime('%d.%m.%Y %H:%M')
        return super(MyJSONEncoder, self).default(obj)