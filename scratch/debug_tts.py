import asyncio
import aiohttp
import edge_tts
from edge_tts.communicate import (
    WSS_URL,
    WSS_HEADERS,
    SEC_MS_GEC_VERSION,
    DRM,
    _SSL_CTX,
    connect_id,
    date_to_string,
    mkssml,
    ssml_headers_plus_data,
)

async def debug_stream():
    text = "Поверь, ночь — это не просто тьма. Она ждет момента, когда ты допустишь ошибку."
    comm = edge_tts.Communicate(text, "ru-RU-DmitryNeural")
    url = f"{WSS_URL}&ConnectionId={connect_id()}&Sec-MS-GEC={DRM.generate_sec_ms_gec()}&Sec-MS-GEC-Version={SEC_MS_GEC_VERSION}"
    headers = DRM.headers_with_muid(WSS_HEADERS)

    async with aiohttp.ClientSession(timeout=comm.session_timeout) as session:
        async with session.ws_connect(url, headers=headers, ssl=_SSL_CTX) as ws:
            cmd = (
                f"X-Timestamp:{date_to_string()}\r\n"
                "Content-Type:application/json; charset=utf-8\r\n"
                "Path:speech.config\r\n\r\n"
                '{"context":{"synthesis":{"audio":{"metadataoptions":{'
                '"sentenceBoundaryEnabled":"true","wordBoundaryEnabled":"false"'
                '},"outputFormat":"audio-24khz-48kbitrate-mono-mp3"}}}}\r\n'
            )
            await ws.send_str(cmd)

            texts = list(comm.texts)
            ssml = mkssml(comm.tts_config, texts[0])
            req = ssml_headers_plus_data(connect_id(), date_to_string(), ssml)
            await ws.send_str(req)
            print("Sent SSML! Waiting for msgs...")

            async for msg in ws:
                print("MSG TYPE:", msg.type)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print("TEXT MSG:", msg.data.replace("\r\n", " | ")[:300])
                    if "turn.end" in msg.data:
                        print("turn.end reached!")
                        break
                elif msg.type == aiohttp.WSMsgType.BINARY:
                    print("BINARY MSG len:", len(msg.data))
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    print("WS CLOSED:", msg.data)
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print("WS ERROR:", msg.data)
                    break
            print("Finished stream. ws.close_code:", ws.close_code, "ws.closed:", ws.closed)

if __name__ == "__main__":
    asyncio.run(debug_stream())
