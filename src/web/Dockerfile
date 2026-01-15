FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm config set strict-ssl false && npm install
RUN npm install @tailwindcss/postcss

COPY . .

ENV NODE_TLS_REJECT_UNAUTHORIZED=0

ARG NEXT_PUBLIC_SKOSMOS_URL
ENV NEXT_PUBLIC_SKOSMOS_URL=$NEXT_PUBLIC_SKOSMOS_URL

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
