from flask_restful import Resource, Api
from flask import request
from backend.models import db, Parking_lot, Parking_spot, Reservation
from datetime import datetime

api = Api()


class LotApi(Resource):
    def get(self):
        lots = Parking_lot.query.all()
        return [{
            'id': lot.id,
            'name': lot.name,
            'address': lot.address,
            'pin_code': lot.pin_code,
            'price_per_hour': lot.price,
            'max_spots': lot.max_spots
        } for lot in lots]

    def post(self):
        data = request.json
        new_lot = Parking_lot(
            name=data.get("name"),
            address=data.get("address"),
            pin_code=data.get("pin_code"),
            price=data.get("price_per_hour"),
            max_spots=data.get("max_spots")
        )
        db.session.add(new_lot)
        db.session.commit()
        return {"message": "New parking lot added!"}, 201

    def put(self, id):
        lot = Parking_lot.query.get(id)
        if lot:
            data = request.json
            lot.name = data.get("name")
            lot.address = data.get("address")
            lot.pin_code = data.get("pin_code")
            lot.price = data.get("price_per_hour")
            lot.max_spots = data.get("max_spots")
            db.session.commit()
            return {"message": "Parking lot updated!"}, 200
        return {"message": "Lot ID not found!"}, 404

    def delete(self, id):
        lot = Parking_lot.query.get(id)
        if lot:
            db.session.delete(lot)
            db.session.commit()
            return {"message": "Parking lot deleted!"}, 200
        return {"message": "Lot ID not found!"}, 404

class LotSearchApi(Resource):
    def get(self, id):
        lot = Parking_lot.query.get(id)
        if lot:
            return [{
                'id': lot.id,
                'name': lot.name,
                'address': lot.address,
                'pin_code': lot.pin_code,
                'price_per_hour': lot.price,
                'max_spots': lot.max_spots
            }]
        return {"message": "Lot ID not found!"}, 404


class SpotApi(Resource):
    def get(self):
        spots = Parking_spot.query.all()
        return [{
            'id': spot.id,
            'lot_id': spot.lot_id,
            'lot_name': spot.parking_lot.name,
            'status': spot.status
        } for spot in spots]

    def post(self):
        data = request.json
        new_spot = Parking_spot(
            lot_id=data.get("lot_id"),
            status=data.get("status")
        )
        db.session.add(new_spot)
        db.session.commit()
        return {"message": "New parking spot added!"}, 201

    def put(self, id):
        spot = Parking_spot.query.get(id)
        if spot:
            data = request.json
            spot.lot_id = data.get("lot_id")
            spot.status = data.get("status")
            db.session.commit()
            return {"message": "Parking spot updated!"}, 200
        return {"message": "Spot ID not found!"}, 404

    def delete(self, id):
        spot = Parking_spot.query.get(id)
        if spot:
            db.session.delete(spot)
            db.session.commit()
            return {"message": "Parking spot deleted!"}, 200
        return {"message": "Spot ID not found!"}, 404

class SpotSearchApi(Resource):
    def get(self, id):
        spot = Parking_spot.query.get(id)
        if spot:
            return [{
                'id': spot.id,
                'lot_id': spot.lot_id,
                'lot_name': spot.parking_lot.name,
                'status': spot.status
            }]
        return {"message": "Spot ID not found!"}, 404


class ReservationApi(Resource):
    def get(self):
        reservations = Reservation.query.all()
        return [{
            "id": r.id,
            "user_id": r.user_id,
            "user_email": r.user.email,
            "lot_id": r.lot_id,
            "lot_name": r.parking_lot.name,
            "spot_id": r.spot_id,
            "spot_status": r.parking_spot.status,
            "start_time": r.start_time.isoformat(),
            "end_time": r.end_time.isoformat(),
            "park_time": r.park_time.isoformat() if r.park_time else None,
            "release_time": r.release_time.isoformat() if r.release_time else None,
            "cost": r.cost
        } for r in reservations]

    def post(self):
        data = request.json
        new_res = Reservation(
            user_id=data.get("user_id"),
            lot_id=data.get("lot_id"),
            spot_id=data.get("spot_id"),
            start_time=datetime.fromisoformat(data.get("start_time")),
            end_time=datetime.fromisoformat(data.get("end_time"))
        )
        db.session.add(new_res)
        db.session.commit()
        return {"message": "New reservation created!"}, 201

    def delete(self, id):
        res = Reservation.query.get(id)
        if res:
            db.session.delete(res)
            db.session.commit()
            return {"message": "Reservation deleted!"}, 200
        return {"message": "Reservation ID not found!"}, 404

class ReservationSearchApi(Resource):
    def get(self, id):
        r = Reservation.query.get(id)
        if r:
            return [{
                "id": r.id,
                "user_id": r.user_id,
                "user_email": r.user.email,
                "lot_id": r.lot_id,
                "lot_name": r.parking_lot.name,
                "spot_id": r.spot_id,
                "spot_status": r.parking_spot.status,
                "start_time": r.start_time.isoformat(),
                "end_time": r.end_time.isoformat(),
                "park_time": r.park_time.isoformat() if r.park_time else None,
                "release_time": r.release_time.isoformat() if r.release_time else None,
                "cost": r.cost
            }]
        return {"message": "Reservation ID not found!"}, 404


api.add_resource(LotApi,  "/api/get_lots", "/api/add_lot", "/api/edit_lot/<int:id>", "/api/delete_lot/<int:id>")

api.add_resource(LotSearchApi, "/api/search_lot/<int:id>")

api.add_resource(SpotApi, "/api/get_spots", "/api/add_spot", "/api/edit_spot/<int:id>", "/api/delete_spot/<int:id>")

api.add_resource(SpotSearchApi, "/api/search_spot/<int:id>")

api.add_resource(ReservationApi, "/api/get_reservations", "/api/add_reservation", "/api/delete_reservation/<int:id>")

api.add_resource(ReservationSearchApi, "/api/search_reservation/<int:id>")

def init_api(app):
    api.init_app(app)