from flask import Flask
from flask_restful import Resource, Api, reqparse, fields, marshal_with
import RPi.GPIO as GPIO

app = Flask(__name__)
api = Api(app)

pin_model = {
    'pin_num': fields.Integer,
    'state': fields.String,
    'pin_mode': fields.String,
}


class PinUtil(object):
    def __init__(self):
        self.counter = 0
        self.pins = []

    def pin_available(self, pin_num):
        for pin in self.pins:
            if pin['pin_num'] == pin_num:
                print(pin_num)
                return True
        return False

    def get(self, pin_num):
        for pin in self.pins:
            if pin['pin_num'] == pin_num:
                return pin
        return False

    def create(self, data):
        pin = data
        self.pins.append(pin)
        print(self.pins)

        if pin['pin_mode'] == 'out':
            GPIO.setup(pin['pin_num'], GPIO.OUT)
            print(f'setup {pin["pin_num"]} as output')
            if pin['state'] == 'off':
                GPIO.output(pin['pin_num'], GPIO.LOW)
                print(f'turn {pin["pin_num"]} off')
            elif pin['state'] == 'on':
                GPIO.output(pin['pin_num'], GPIO.HIGH)
                print(f'turn {pin["pin_num"]} on')

        if pin['pin_mode'] == 'in':
            GPIO.setup(pin['pin_num'], GPIO.IN)
            print(f'setup {pin["pin_num"]} as input')
            pin['state'] = GPIO.input(pin['pin_num'])

        return pin

    def update(self, pin_num, data):
        pin = self.get(pin_num)
        print(data, "data")

        if data['pin_mode'] == 'out':
            GPIO.setup(pin['pin_num'], GPIO.OUT)
            print(f'setup {pin["pin_num"]} as output')

            if data['state'] == 'off':
                GPIO.output(pin['pin_num'], GPIO.LOW)
                print(f'turn {pin["pin_num"]} off')
            elif data['state'] == 'on':
                GPIO.output(pin['pin_num'], GPIO.HIGH)
                print(f'turn {pin["pin_num"]} on')
            pin.update(data)  # this is the dict_object update method

        if data['pin_mode'] == "in":
            GPIO.setup(pin['pin_num'], GPIO.IN)
            print(f'setup {pin["pin_num"]} as input')
            pin['state'] = GPIO.input(pin['pin_num'])
            data.pop('state') # so you cant change state of input pin
            pin.update(data)

        return pin

    def delete(self, pin_num):
        pin = self.get(pin_num)

        if pin['pin_mode'] == 'out':
            GPIO.output(pin['pin_num'], GPIO.LOW)
            pass
        print(f'delete {pin["pin_num"]} from the list')
        self.pins.remove(pin)


parser = reqparse.RequestParser()
parser.add_argument('pin_num', type=int, help='pin number (BCM)', )
parser.add_argument('pin_mode', type=str, help='pin mode (in or out)', choices=['in', 'out'])
parser.add_argument('state', type=str, help='Content of the pin (on or off)', choices=['on', 'off'])


class PinList(Resource):
    """Shows a list of all pins, and lets you POST to add new pins"""

    @marshal_with(pin_model)
    def get(self):
        """List all pins"""
        return list(pin_util.pins)


class Pin(Resource):
    """Show a single pin item and lets you update/delete them"""

    @marshal_with(pin_model)
    def post(self, pin_id):
        args = parser.parse_args()
        args['pin_num'] = pin_id
        if pin_util.pin_available(pin_id):
            print("test")
            return f"{pin_id} is already created", 409
        return pin_util.create(args), 200

    def get(self, pin_id):
        """Fetch a pin given its resource identifier"""
        if pin_util.pin_available(pin_id):
            return pin_util.get(pin_id), 200
        return {"error": f"pin {pin_id} not available"}, 404


    @marshal_with(pin_model)
    def put(self, pin_id):
        """Update a pin given its identifier"""
        args = parser.parse_args()
        args['pin_num'] = pin_id
        if pin_util.pin_available(pin_id):
            return pin_util.update(pin_id, args), 200
        else:
            return {'message': 'Pin not found'}, 404


    def delete(self, pin_id):
        """Delete a pin given its identifier"""
        if pin_util.pin_available(pin_id):
            pin_util.delete(pin_id)
            return f'{pin_id} removed successful', 204
        return {'message': 'Pin not found'}, 404  # Returning a response with status code 404


api.add_resource(PinList, '/pins')
api.add_resource(Pin, '/pins/<int:pin_id>')

GPIO.setmode(GPIO.BCM)

pin_util = PinUtil()
pin_util.create({'pin_num': 23, 'pin_mode': 'out', 'state': 'off'})
pin_util.create({'pin_num': 24, 'pin_mode': 'out', 'state': 'off'})
pin_util.create({'pin_num': 25, 'pin_mode': 'out', 'state': 'off'})
pin_util.create({'pin_num': 22, 'pin_mode': 'out', 'state': 'off'})
pin_util.create({'pin_num': 12, 'pin_mode': 'out', 'state': 'off'})
pin_util.create({'pin_num': 16, 'pin_mode': 'out', 'state': 'off'})
pin_util.create({'pin_num': 20, 'pin_mode': 'out', 'state': 'off'})
pin_util.create({'pin_num': 21, 'pin_mode': 'out', 'state': 'off'})
pin_util.create({'pin_num': 13, 'pin_mode': 'out', 'state': 'off'})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")