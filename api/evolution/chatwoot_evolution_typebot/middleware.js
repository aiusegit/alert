require('dotenv').config();
const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

app.post('/webhook', async (req, res) => {
  const { event } = req.body;
  if (event === 'message.created') {
    try {
      // Lógica para rotear a mensagem para a Evolution API
      await axios.post(`${process.env.EVOLUTION_API_URL}/webhook/instance`, req.body);
      // Lógica para rotear a mensagem para o Typebot
      await axios.post(process.env.TYPEBOT_URL, req.body);
      console.log('Mensagem roteada com sucesso');
    } catch (error) {
      console.error('Erro ao rotear a mensagem:', error);
    }
  }
  res.status(200).send('Webhook recebido');
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Middleware ouvindo na porta ${PORT}`);
});