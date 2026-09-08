FROM mcr.microsoft.com/playwright:v1.51.1-noble
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
CMD ["npx", "playwright", "test", "--config=playwright.config.js"]

