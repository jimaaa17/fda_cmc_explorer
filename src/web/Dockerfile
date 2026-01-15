FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm config set strict-ssl false && npm install
RUN npm install @tailwindcss/postcss

COPY . .

ENV NODE_TLS_REJECT_UNAUTHORIZED=0
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
