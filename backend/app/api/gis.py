from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import LandRecord
from backend.app.services.auth import get_current_user

router = APIRouter(prefix="/api/gis", tags=["GIS & Cadastral Mapping"])


@router.get("/parcels")
def get_cadastral_parcels(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Returns Cadastral GIS parcel polygons aligned with BhuNaksha / LandLens standards.
    Links digitized Khasra land records with cadastral GIS plot vectors.
    """
    import os, json
    records = db.query(LandRecord).all()
    record_map = {r.khasra_number: r for r in records if r.khasra_number}

    # Check for ingested real Cadastral GeoJSON dataset
    geojson_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "datasets", "cadastral_parcels", "cadastral_parcels.geojson")
    )

    if os.path.exists(geojson_path):
        try:
            with open(geojson_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            features = data.get("features", [])
            for feat in features:
                props = feat.get("properties", {})
                kh = props.get("khasra_number")
                if kh in record_map:
                    rec = record_map[kh]
                    props["owner_name"] = rec.owner_name
                    props["status"] = rec.verification_status
                    props["record_id"] = rec.id
                    props["matched"] = True
                else:
                    props["owner_name"] = props.get("owner_name", "Unregistered / Reserved")
                    props["status"] = "unregistered"
                    props["record_id"] = None
                    props["matched"] = False
            return {
                "type": "FeatureCollection",
                "features": features,
                "source": "BhuNaksha Cadastral Vectors",
                "total_parcels": len(features)
            }
        except Exception:
            pass

    # Fallback to local default parcels
    base_parcels = [
        {
            "khasra": "245/2",
            "village": "Rau",
            "tehsil": "Rau",
            "coords": [
                [75.810, 22.630],
                [75.814, 22.630],
                [75.814, 22.634],
                [75.810, 22.634],
                [75.810, 22.630],
            ],
        },
        {
            "khasra": "245/1",
            "village": "Rau",
            "tehsil": "Rau",
            "coords": [
                [75.814, 22.630],
                [75.818, 22.630],
                [75.818, 22.634],
                [75.814, 22.634],
                [75.814, 22.630],
            ],
        },
        {
            "khasra": "318/1",
            "village": "Kanadia",
            "tehsil": "Kanadia",
            "coords": [
                [75.820, 22.636],
                [75.826, 22.636],
                [75.826, 22.641],
                [75.820, 22.641],
                [75.820, 22.636],
            ],
        },
        {
            "khasra": "102/3",
            "village": "Mangliya",
            "tehsil": "Sanwer",
            "coords": [
                [75.805, 22.624],
                [75.809, 22.624],
                [75.809, 22.628],
                [75.805, 22.628],
                [75.805, 22.624],
            ],
        },
    ]

    features = []
    for p in base_parcels:
        khasra = p["khasra"]
        rec = record_map.get(khasra)

        owner = rec.owner_name if rec else "Pending Digitization"
        status = rec.verification_status if rec else "unregistered"
        area = rec.land_area if rec else "1.0 Ha (Est.)"

        features.append(
            {
                "type": "Feature",
                "properties": {
                    "khasra_number": khasra,
                    "village": p["village"],
                    "tehsil": p["tehsil"],
                    "district": "Indore",
                    "state": "Madhya Pradesh",
                    "owner_name": owner,
                    "land_area": area,
                    "status": status,
                    "record_id": rec.id if rec else None,
                    "is_demo": True,
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [p["coords"]],
                },
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
        "disclaimer": "Synthetic Cadastral Boundaries for Demonstration Purposes Only",
    }
