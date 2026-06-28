from fastapi import APIRouter, Request, Query

from app.schemas.response import ApiResponse

router = APIRouter(prefix="/org", tags=["Organization"])


@router.get("/ou-tree")
async def get_ou_tree(request: Request):
    from app.core.deps import get_ou_repo
    repo = await get_ou_repo(request)
    ous = await repo.get_tree()
    return ApiResponse(data=[{"dn": o.dn, "ou_name": o.ou_name, "parent_dn": o.parent_dn, "site_code": o.site_code} for o in ous])


@router.get("/ous/{ou_dn:path}")
async def get_ou(request: Request, ou_dn: str):
    from app.core.deps import get_ou_repo
    repo = await get_ou_repo(request)
    ou = await repo.get_by_dn(ou_dn)
    if ou:
        return ApiResponse(data={"dn": ou.dn, "ou_name": ou.ou_name, "parent_dn": ou.parent_dn, "site_code": ou.site_code, "description": ou.description})
    return ApiResponse(code=404, message="OU not found")


@router.get("/users")
async def list_users(
    request: Request,
    ou_dn: str | None = None,
    site_code: str | None = None,
    department: str | None = None,
    is_enabled: bool | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    from app.core.deps import get_user_repo
    repo = await get_user_repo(request)
    users, total = await repo.list_users(ou_dn=ou_dn, site_code=site_code, department=department, is_enabled=is_enabled, search=search, page=page, page_size=page_size)
    return ApiResponse(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{"sid": u.sid, "username": u.username, "display_name": u.display_name, "email": u.email, "department": u.department, "is_enabled": u.is_enabled, "site_code": u.site_code} for u in users],
    })


@router.get("/users/{user_sid}")
async def get_user(request: Request, user_sid: str):
    from app.core.deps import get_user_repo
    repo = await get_user_repo(request)
    user = await repo.get_by_sid(user_sid)
    if user:
        return ApiResponse(data={"sid": user.sid, "username": user.username, "display_name": user.display_name, "email": user.email, "department": user.department, "ou_dn": user.ou_dn, "is_enabled": user.is_enabled, "is_locked": user.is_locked})
    return ApiResponse(code=404, message="User not found")


@router.get("/groups")
async def list_groups(request: Request, ou_dn: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200)):
    from app.core.deps import get_group_repo
    repo = await get_group_repo(request)
    groups, total = await repo.list_groups(ou_dn=ou_dn, page=page, page_size=page_size)
    return ApiResponse(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{"dn": g.dn, "group_name": g.group_name, "scope": g.scope, "category": g.category, "description": g.description} for g in groups],
    })


@router.get("/groups/{group_dn:path}")
async def get_group(request: Request, group_dn: str):
    from app.core.deps import get_group_repo
    repo = await get_group_repo(request)
    group = await repo.get_by_dn(group_dn)
    if group:
        members = await repo.get_members(group_dn)
        return ApiResponse(data={"dn": group.dn, "group_name": group.group_name, "scope": group.scope, "members": [{"member_dn": m.member_dn, "member_sid": m.member_sid, "member_type": m.member_type} for m in members]})
    return ApiResponse(code=404, message="Group not found")


@router.post("/groups/{group_dn:path}/members")
async def add_group_member(request: Request, group_dn: str):
    from app.core.deps import get_group_repo
    repo = await get_group_repo(request)
    body = await request.json()
    member = await repo.add_member(group_dn, body["member_dn"], body.get("member_sid"), body.get("member_type", "user"))
    return ApiResponse(data={"member_dn": member.member_dn})


@router.delete("/groups/{group_dn:path}/members/{member_dn:path}")
async def remove_group_member(request: Request, group_dn: str, member_dn: str):
    from app.core.deps import get_group_repo
    repo = await get_group_repo(request)
    success = await repo.remove_member(group_dn, member_dn)
    return ApiResponse(data={"success": success})