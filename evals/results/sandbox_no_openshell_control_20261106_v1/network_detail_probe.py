import os,socket,time,urllib.request
t=time.time()
try: socket.create_connection(("169.254.169.254",80),timeout=5); print("metadata: connected")
except OSError as e: print("metadata:",type(e).__name__,e,round(time.time()-t,1),"s")
try: r=urllib.request.urlopen("https://huggingface.co",timeout=10); print("huggingface: HTTP",r.status)
except Exception as e: print("huggingface:",type(e).__name__,e)
try: print("listdir /home:",os.listdir("/home"))
except OSError as e: print("listdir /home:",type(e).__name__,e)
