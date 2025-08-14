from .base_router import *


def get_gateway_router(db: DataBase) -> APIRouter:
    router = APIRouter()
    sessions_manager = SessionsManager()
    jwt_parser = JwtParser()
    base_router = BaseRouter(db)
    auth_service = AuthService(db)


    @router.api_route("/{endpoint_path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS","HEAD"])
    async def proxy(
        endpoint_path: str,
        request: Request,
        token: Optional[str] = Depends(base_router.get_bearer_token),
    ):
        if not base_router.is_public_endpoint(request.method, endpoint_path):
            if not token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization")

            token_payload = auth_service.validate_access_token(token)
            if not token_payload:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        service_address = base_router.map_path_to_service_address(endpoint_path)
        if not service_address:
            raise HTTPException(status_code=404, detail="No upstream service mapped for this path")

        final_forward_url = f"{service_address}/{endpoint_path}"

        parsed = urlparse(final_forward_url)
        upstream_host = parsed.netloc
        client_host = request.client.host if request.client else None
        incoming_headers = dict(request.headers)
        headers = base_router.filter_request_headers(incoming_headers, upstream_host=upstream_host, client_ip=client_host)

        if "authorization" in incoming_headers:
            headers["Authorization"] = incoming_headers["authorization"]
        body = await request.body()
        params = dict(request.query_params)

        try:
            response = await base_router.client.request(
                method=request.method,
                url=final_forward_url,
                headers=headers,
                content=body if body else None,
                params=params,
                timeout=httpx.Timeout(10.0, read=30.0),
            )

        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Upstream request failed: {exc}") from exc

        response_headers = base_router.filter_response_headers(response.headers)
        
        return Response(content=response.content, status_code=response.status_code, headers=response_headers)



    return router


