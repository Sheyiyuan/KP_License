from api.api import license_app
import uvicorn
from core.core import conf
PORT = conf.get()["api"]["port"]

if __name__ == '__main__':
    uvicorn.run(license_app, host='0.0.0.0', port=PORT)