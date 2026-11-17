FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Run Vite in dev mode so we can live-edit from host
CMD ["npm", "run", "dev", "--", "--host"]
