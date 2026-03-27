from fastapi import HTTPException
from bson import ObjectId


@router.patch("/{project_id}", response_model=ProjectInDB)
async def update_project(
    project_id: str,
    updates: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    user_id = current_user["sub"]

    existing = await db_module.database["projects"].find_one(
        {"_id": ObjectId(project_id)}
    )

    if not existing:
        raise HTTPException(status_code=404, detail="Project not found")

    if existing["owner_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    updates["updated_at"] = datetime.now(timezone.utc)

    await db_module.database["projects"].update_one(
        {"_id": ObjectId(project_id)},
        {"$set": updates},
    )

    updated = await db_module.database["projects"].find_one(
        {"_id": ObjectId(project_id)}
    )

    return ProjectInDB(
        id=str(updated["_id"]),
        name=updated["name"],
        description=updated.get("description"),
        owner_id=updated["owner_id"],
        status=updated["status"],
        members=updated.get("members", []),
        tags=updated.get("tags", []),
        created_at=updated["created_at"],
        updated_at=updated["updated_at"],
    )
@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    user_id = current_user["sub"]

    existing = await db_module.database["projects"].find_one(
        {"_id": ObjectId(project_id)}
    )

    if not existing:
        raise HTTPException(status_code=404, detail="Project not found")

    if existing["owner_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db_module.database["projects"].delete_one(
        {"_id": ObjectId(project_id)}
    )

    return {"status": "deleted"}
