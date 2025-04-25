FROM node:16

WORKDIR /usr/src/iotapp/backend

COPY package*.json ./
RUN npm install

COPY . .

# 3000번 포트 열기
EXPOSE 3000

# 애플리케이션 실행
CMD ["node", "server.js"]
