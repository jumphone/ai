
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

    print('-'*20+'-|-BLOCK-|-'+'-'*20+'\n'+TIMESTAMP+':')

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

    # 5. 获取并打印 Request Body
    body = await request.body()
    
    print("<request_body>")
    try:
        # 尝试作为 JSON 打印（美化格式）
        if body:
            payload = json.loads(body)
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print("[Empty Body]")
    except Exception:
        # 如果不是 JSON，则直接打印原始字节（转字符串）
        print(body.decode("utf-8", errors="ignore"))
    print("</request_body>")

    # 发送请求 (注意：这里直接传入上面已经读取好的 body)
    resp = await client.request(
        method=request.method,
        url=final_url,
        headers=headers,
        content=body,  # 确保使用的是我们 await 过的 body
        params=request.query_params,
        timeout=60.0
    )

    # 6. 构造返回 (简化生成器，移除服务端打印逻辑)
    async def content_generator():
        # 直接转发字节流，不做任何解析和打印
        async for chunk in resp.aiter_bytes():
            yield chunk

    # 7. 构造返回 Headers (过滤掉会导致解析错误的 header)
    excluded_full_headers = ["content-encoding", "transfer-encoding", "content-length"]
    resp_headers = {
        k: v for k, v in resp.headers.items() 
        if k.lower() not in excluded_full_headers
    }

    return StreamingResponse(
        content_generator(), # 现在它只负责安静地转发数据
        status_code=resp.status_code,
        headers=resp_headers,
        media_type=resp.headers.get("content-type")
    )

    '''
    # 6. 构造返回 Headers (过滤掉会导致解析错误的 header)
    async def content_generator():
        print("Response:")
        async for chunk in resp.aiter_bytes():
            yield chunk  # 这一行必须保留，负责把数据发回给前端
            
            # --- 以下是最小化打印逻辑 ---
            try:
                chunk_str = chunk.decode("utf-8", errors="ignore")
                # 针对 SSE 格式进行拆分处理
                for line in chunk_str.split('\n'):
                    if line.startswith("data: ") and "[DONE]" not in line:
                        data = json.loads(line[6:])
                        delta = data['choices'][0].get('delta', {})
                        
                        # 重点：兼容 reasoning_content (思考) 和 content (回答)
                        content = delta.get('reasoning_content') or delta.get('content') or ""
                        if content:
                            print(content, end="", flush=True) # 像打字机一样流式显示
            except:
                pass # 忽略解析失败的碎片内容

    # 7. 构造返回 (使用我们包装后的生成器)
    excluded_full_headers = ["content-encoding", "transfer-encoding", "content-length"]
    resp_headers = {
        k: v for k, v in resp.headers.items() 
        if k.lower() not in excluded_full_headers
    }

    return StreamingResponse(
        content_generator(), # 使用包装后的生成器
        status_code=resp.status_code,
        headers=resp_headers,
        media_type=resp.headers.get("content-type")
    )
    '''
