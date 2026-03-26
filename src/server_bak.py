
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx, json
from .config import *
from datetime import datetime

# ==================== 配置 ====================
PROXY_API_KEY = [open(PROXY_KEY_FILE).read().rstrip()] #分发Key
REAL_API_KEY = open(REAL_KEY_FILE).read().rstrip() # 真实Key（服务器私有）
 

# ==============================================
app = FastAPI(title="OpenAI 安全代理服务")
client = httpx.AsyncClient()

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path: str):

    print('<'+TIMESTAMP+'>')

    print('<request>')
    print(request)
    print('</request>')

    print('<path>')
    print(path)
    print('</path>')

    # 1. 提取 Token (兼容大小写)
    auth = request.headers.get("Authorization") or request.headers.get("authorization", "")
    user_token = auth.replace("Bearer ", "").strip()

    # 2. 校验 Token
    if user_token not in PROXY_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid Token")

    # 3. 构造转发 URL (防止 v1/v1)
    # API_URL = 'https://api.moonshot.cn/v1'
    base_url = API_URL.rstrip('/')
    clean_path = path.lstrip('/')
    
    # 如果 path 以 v1 开头，去掉它，因为 API_URL 里已经有了
    if clean_path.startswith("v1/"):
        final_url = f"{base_url}/{clean_path[3:]}"
    else:
        final_url = f"{base_url}/{clean_path}"

    # 4. 准备 Headers
    headers = {k.lower(): v for k, v in request.headers.items()}
    # 必须删除的 Header
    for drop_key in ["host", "content-length", "authorization", "accept-encoding"]:
        headers.pop(drop_key, None)
    
    # 注入真实 Key
    headers["authorization"] = f"Bearer {REAL_API_KEY}"

    # 5. 发送请求
    body = await request.body()
    resp = await client.request(
        method=request.method,
        url=final_url,
        headers=headers,
        content=body,
        params=request.query_params,
        timeout=60.0 # 建议给个超时
    )

    # 6. 构造返回 Headers (过滤掉会导致解析错误的 header)
    excluded_full_headers = ["content-encoding", "transfer-encoding", "content-length"]
    resp_headers = {
        k: v for k, v in resp.headers.items() 
        if k.lower() not in excluded_full_headers
    }
    output=StreamingResponse(
        resp.aiter_bytes(),
        status_code=resp.status_code,
        headers=resp_headers,
        media_type=resp.headers.get("content-type")
        )

    print("<output>")
    print(output)
    print('</output>')

    print("</"+TIMESTAMP+">")
    return output
