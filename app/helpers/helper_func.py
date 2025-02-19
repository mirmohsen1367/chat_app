from fastapi.exceptions import HTTPException


def get_or_404(db, model, id):
    obj = db.query(model).filter(model.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return obj
