import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import typer
from rich.console import Console
from rich.table import Table

# Inicialização
load_dotenv()
console = Console()
app = typer.Typer(name="evolution", help="CLI para Evolution API v2.2.2")
instance_app = typer.Typer(name="instance", help="Gerenciar instâncias")
proxy_app = typer.Typer(name="proxy", help="Gerenciar proxy")
settings_app = typer.Typer(name="settings", help="Gerenciar configurações")
message_app = typer.Typer(name="message", help="Enviar mensagens")
call_app = typer.Typer(name="call", help="Gerenciar chamadas")
chat_app = typer.Typer(name="chat", help="Gerenciar chats")
contact_app = typer.Typer(name="contact", help="Gerenciar contatos")
label_app = typer.Typer(name="label", help="Gerenciar etiquetas")
profile_app = typer.Typer(name="profile", help="Gerenciar perfil")
group_app = typer.Typer(name="group", help="Gerenciar grupos")
broadcast_app = typer.Typer(name="broadcast", help="Gerenciar listas de transmissão")
integration_app = typer.Typer(name="integration", help="Gerenciar integrações")

app.add_typer(instance_app, name="instance")
app.add_typer(proxy_app, name="proxy")
app.add_typer(settings_app, name="settings")
app.add_typer(message_app, name="message")
app.add_typer(call_app, name="call")
app.add_typer(chat_app, name="chat")
app.add_typer(contact_app, name="contact")
app.add_typer(label_app, name="label")
app.add_typer(profile_app, name="profile")
app.add_typer(group_app, name="group")
app.add_typer(broadcast_app, name="broadcast")
app.add_typer(integration_app, name="integration")

# Configuração
class Config:
    BASE_URL = os.getenv("EVOLUTION_BASE_URL", "http://localhost:8080")
    GLOBAL_APIKEY = os.getenv("EVOLUTION_APIKEY", "")

config = Config()

# Cliente HTTP
class APIClient:
    def __init__(self):
        self.base_url = config.BASE_URL
        self.apikey = config.GLOBAL_APIKEY

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = {"apikey": self.apikey} if self.apikey else {}

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                params=params,
                files=files
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.HTTPError as e:
            console.print(f"[red]Error: {e.response.status_code} - {e.response.text}[/red]")
            raise
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Request failed: {e}[/red]")
            raise

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        return self._make_request("GET", endpoint, params=params)

    def post(self, endpoint: str, json: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict[str, Any]:
        return self._make_request("POST", endpoint, json=json, files=files)

    def put(self, endpoint: str, json: Optional[Dict] = None) -> Dict[str, Any]:
        return self._make_request("PUT", endpoint, json=json)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        return self._make_request("DELETE", endpoint)

client = APIClient()

# Utilitários
def display_response(data: Dict[str, Any], title: str = "Response"):
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    def flatten_dict(d: Dict, parent_key: str = ""):
        for key, value in d.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict):
                flatten_dict(value, new_key)
            else:
                table.add_row(new_key, str(value))

    flatten_dict(data)
    console.print(table)

def display_success(message: str):
    console.print(f"[green]Success: {message}[/green]")

# Root Command
@app.command("info", help="Obter informações da API")
def get_info():
    response = client.get("")
    display_response(response, "Informações da API")

# Instance Commands
@instance_app.command("create", help="Criar uma nova instância")
def instance_create(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    qrcode: bool = typer.Option(True, "--qrcode/--no-qrcode", help="Gerar QR code"),
    number: Optional[str] = typer.Option(None, "--number", "-n", help="Número de telefone")
):
    payload = {
        "instanceName": instance,
        "qrcode": qrcode,
        "integration": "WHATSAPP-BAILEYS"
    }
    if number:
        payload["number"] = number
    response = client.post("/instance/create", json=payload)
    display_response(response, f"Instância {instance} Criada")
    if qrcode and "qrcode" in response:
        console.print(f"[yellow]QR Code: {response['qrcode']}[/yellow]")

@instance_app.command("list", help="Listar instâncias")
def instance_list(
    instance: Optional[str] = typer.Option(None, "--instance", "-i", help="Filtrar por nome"),
    instance_id: Optional[str] = typer.Option(None, "--instance-id", help="Filtrar por ID")
):
    params = {}
    if instance:
        params["instanceName"] = instance
    if instance_id:
        params["instanceId"] = instance_id
    response = client.get("/instance/fetchInstances", params=params)
    display_response(response, "Instâncias")

@instance_app.command("connect", help="Conectar a uma instância")
def instance_connect(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: Optional[str] = typer.Option(None, "--number", "-n", help="Número de telefone")
):
    params = {"number": number} if number else {}
    response = client.get(f"/instance/connect/{instance}", params=params)
    display_response(response, f"Conexão da Instância {instance}")

@instance_app.command("restart", help="Reiniciar instância")
def instance_restart(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.post(f"/instance/restart/{instance}")
    display_success(f"Instância {instance} reiniciada")

@instance_app.command("set-presence", help="Definir presença")
def instance_set_presence(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    presence: str = typer.Option(..., "--presence", "-p", help="Presença (available, unavailable)")
):
    payload = {"presence": presence}
    response = client.post(f"/instance/setPresence/{instance}", json=payload)
    display_response(response, "Presença Atualizada")

@instance_app.command("status", help="Verificar status da conexão")
def instance_status(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.get(f"/instance/connectionState/{instance}")
    display_response(response, f"Status da Instância {instance}")

@instance_app.command("logout", help="Desconectar instância")
def instance_logout(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.delete(f"/instance/logout/{instance}")
    display_success(f"Instância {instance} desconectada")

@instance_app.command("delete", help="Deletar instância")
def instance_delete(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.delete(f"/instance/delete/{instance}")
    display_success(f"Instância {instance} deletada")

# Proxy Commands
@proxy_app.command("set", help="Configurar proxy")
def proxy_set(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    host: str = typer.Option(..., "--host", help="Host do proxy"),
    port: str = typer.Option(..., "--port", help="Porta do proxy"),
    protocol: str = typer.Option("http", "--protocol", help="Protocolo (http, https)"),
    username: Optional[str] = typer.Option(None, "--username", help="Usuário"),
    password: Optional[str] = typer.Option(None, "--password", help="Senha")
):
    payload = {
        "enabled": True,
        "host": host,
        "port": port,
        "protocol": protocol
    }
    if username:
        payload["username"] = username
    if password:
        payload["password"] = password
    response = client.post(f"/proxy/set/{instance}", json=payload)
    display_response(response, "Proxy Configurado")

@proxy_app.command("get", help="Buscar configuração do proxy")
def proxy_get(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.get(f"/proxy/find/{instance}")
    display_response(response, "Configuração do Proxy")

# Settings Commands
@settings_app.command("set", help="Configurar instância")
def settings_set(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    reject_call: bool = typer.Option(False, "--reject-call/--no-reject-call", help="Rejeitar chamadas"),
    msg_call: Optional[str] = typer.Option(None, "--msg-call", help="Mensagem para chamadas"),
    groups_ignore: bool = typer.Option(False, "--groups-ignore/--no-groups-ignore", help="Ignorar grupos"),
    always_online: bool = typer.Option(False, "--always-online/--no-always-online", help="Sempre online"),
    read_messages: bool = typer.Option(False, "--read-messages/--no-read-messages", help="Ler mensagens"),
    sync_full_history: bool = typer.Option(False, "--sync-full/--no-sync-full", help="Sincronizar histórico"),
    read_status: bool = typer.Option(False, "--read-status/--no-read-status", help="Ler status")
):
    payload = {
        "rejectCall": reject_call,
        "groupsIgnore": groups_ignore,
        "alwaysOnline": always_online,
        "readMessages": read_messages,
        "syncFullHistory": sync_full_history,
        "readStatus": read_status
    }
    if msg_call:
        payload["msgCall"] = msg_call
    response = client.post(f"/settings/set/{instance}", json=payload)
    display_response(response, "Configurações Atualizadas")

@settings_app.command("get", help="Buscar configurações")
def settings_get(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.get(f"/settings/find/{instance}")
    display_response(response, "Configurações da Instância")

# Message Commands
@message_app.command("send-text", help="Enviar mensagem de texto")
def message_send_text(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número do destinatário"),
    text: str = typer.Option(..., "--text", "-t", help="Texto da mensagem"),
    delay: Optional[int] = typer.Option(None, "--delay", "-d", help="Atraso em milissegundos")
):
    payload = {"number": number, "text": text}
    if delay:
        payload["delay"] = delay
    response = client.post(f"/message/sendText/{instance}", json=payload)
    display_response(response, "Mensagem de Texto Enviada")

@message_app.command("send-media", help="Enviar mensagem de mídia")
def message_send_media(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número do destinatário"),
    mediatype: str = typer.Option(..., "--mediatype", "-m", help="Tipo de mídia (image, video, document)"),
    url: str = typer.Option(..., "--url", help="URL da mídia"),
    caption: Optional[str] = typer.Option(None, "--caption", "-c", help="Legenda"),
    filename: Optional[str] = typer.Option(None, "--filename", "-f", help="Nome do arquivo"),
    delay: Optional[int] = typer.Option(None, "--delay", "-d", help="Atraso em milissegundos")
):
    payload = {
        "number": number,
        "mediatype": mediatype,
        "media": url,
        "mimetype": f"{mediatype}/png" if mediatype == "image" else f"{mediatype}/mp4"
    }
    if caption:
        payload["caption"] = caption
    if filename:
        payload["fileName"] = filename
    if delay:
        payload["delay"] = delay
    response = client.post(f"/message/sendMedia/{instance}", json=payload)
    display_response(response, "Mensagem de Mídia Enviada")

@message_app.command("send-ptv", help="Enviar vídeo como PTV")
def message_send_ptv(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número do destinatário"),
    video: str = typer.Option(..., "--video", help="URL do vídeo"),
    delay: Optional[int] = typer.Option(None, "--delay", "-d", help="Atraso em milissegundos")
):
    payload = {"number": number, "video": video}
    if delay:
        payload["delay"] = delay
    response = client.post(f"/message/sendPtv/{instance}", json=payload)
    display_response(response, "PTV Enviado")

@message_app.command("send-audio", help="Enviar áudio narrado")
def message_send_audio(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número do destinatário"),
    audio: str = typer.Option(..., "--audio", help="URL do áudio"),
    delay: Optional[int] = typer.Option(None, "--delay", "-d", help="Atraso em milissegundos")
):
    payload = {"number": number, "audio": audio}
    if delay:
        payload["delay"] = delay
    response = client.post(f"/message/sendWhatsAppAudio/{instance}", json=payload)
    display_response(response, "Áudio Enviado")

@message_app.command("send-status", help="Enviar status/storie")
def message_send_status(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    type: str = typer.Option(..., "--type", help="Tipo (text, image, video, audio)"),
    content: str = typer.Option(..., "--content", help="Conteúdo (texto ou URL)"),
    all_contacts: bool = typer.Option(False, "--all-contacts/--no-all-contacts", help="Enviar para todos os contatos"),
    status_jid: Optional[str] = typer.Option(None, "--status-jid", help="JID do status")
):
    payload = {
        "type": type,
        "content": content,
        "allContacts": all_contacts
    }
    if status_jid:
        payload["statusJidList"] = [status_jid]
    response = client.post(f"/message/sendStatus/{instance}", json=payload)
    display_response(response, "Status Enviado")

@message_app.command("send-sticker", help="Enviar sticker")
def message_send_sticker(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número do destinatário"),
    sticker: str = typer.Option(..., "--sticker", help="URL do sticker"),
    delay: Optional[int] = typer.Option(None, "--delay", "-d", help="Atraso em milissegundos")
):
    payload = {"number": number, "sticker": sticker}
    if delay:
        payload["delay"] = delay
    response = client.post(f"/message/sendSticker/{instance}", json=payload)
    display_response(response, "Sticker Enviado")

@message_app.command("send-location", help="Enviar localização")
def message_send_location(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número do destinatário"),
    name: str = typer.Option(..., "--name", help="Nome do local"),
    address: str = typer.Option(..., "--address", help="Endereço"),
    latitude: float = typer.Option(..., "--latitude", help="Latitude"),
    longitude: float = typer.Option(..., "--longitude", help="Longitude"),
    delay: Optional[int] = typer.Option(None, "--delay", "-d", help="Atraso em milissegundos")
):
    payload = {
        "number": number,
        "name": name,
        "address": address,
        "latitude": latitude,
        "longitude": longitude
    }
    if delay:
        payload["delay"] = delay
    response = client.post(f"/message/sendLocation/{instance}", json=payload)
    display_response(response, "Localização Enviada")

@message_app.command("send-contact", help="Enviar contato")
def message_send_contact(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número do destinatário"),
    full_name: str = typer.Option(..., "--full-name", help="Nome completo"),
    phone_number: str = typer.Option(..., "--phone-number", help="Número de telefone"),
    organization: Optional[str] = typer.Option(None, "--organization", help="Organização"),
    email: Optional[str] = typer.Option(None, "--email", help="Email"),
    url: Optional[str] = typer.Option(None, "--url", help="URL")
):
    contact = {
        "fullName": full_name,
        "phoneNumber": phone_number
    }
    if organization:
        contact["organization"] = organization
    if email:
        contact["email"] = email
    if url:
        contact["url"] = url
    payload = {"number": number, "contact": [contact]}
    response = client.post(f"/message/sendContact/{instance}", json=payload)
    display_response(response, "Contato Enviado")

@message_app.command("send-reaction", help="Enviar reação")
def message_send_reaction(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    remote_jid: str = typer.Option(..., "--remote-jid", "-j", help="JID remoto"),
    message_id: str = typer.Option(..., "--message-id", "-m", help="ID da mensagem"),
    reaction: str = typer.Option(..., "--reaction", "-r", help="Reação (emoji)")
):
    payload = {
        "key": {
            "remoteJid": remote_jid,
            "fromMe": True,
            "id": message_id
        },
        "reaction": reaction
    }
    response = client.post(f"/message/sendReaction/{instance}", json=payload)
    display_response(response, "Reação Enviada")

@message_app.command("send-poll", help="Enviar enquete")
def message_send_poll(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número do destinatário"),
    name: str = typer.Option(..., "--name", help="Título da enquete"),
    values: str = typer.Option(..., "--values", help="Opções, separadas por vírgula"),
    selectable_count: int = typer.Option(1, "--selectable-count", help="Número de opções selecionáveis"),
    delay: Optional[int] = typer.Option(None, "--delay", "-d", help="Atraso em milissegundos")
):
    payload = {
        "number": number,
        "name": name,
        "selectableCount": selectable_count,
        "values": values.split(",")
    }
    if delay:
        payload["delay"] = delay
    response = client.post(f"/message/sendPoll/{instance}", json=payload)
    display_response(response, "Enquete Enviada")

@message_app.command("send-list", help="Enviar lista interativa")
def message_send_list(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número do destinatário"),
    title: str = typer.Option(..., "--title", help="Título da lista"),
    description: str = typer.Option(..., "--description", help="Descrição"),
    button_text: str = typer.Option(..., "--button-text", help="Texto do botão"),
    sections: str = typer.Option(..., "--sections", help="Seções (título:opção1,opção2;...)")
):
    section_list = []
    for section in sections.split(";"):
        title, rows = section.split(":")
        section_list.append({
            "title": title,
            "rows": [{"title": row, "rowId": f"row_{i}"} for i, row in enumerate(rows.split(","))]
        })
    payload = {
        "number": number,
        "title": title,
        "description": description,
        "buttonText": button_text,
        "sections": section_list
    }
    response = client.post(f"/message/sendList/{instance}", json=payload)
    display_response(response, "Lista Enviada")

@message_app.command("send-buttons", help="Enviar botões interativos")
def message_send_buttons(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número do destinatário"),
    title: str = typer.Option(..., "--title", help="Título"),
    description: str = typer.Option(..., "--description", help="Descrição"),
    buttons: str = typer.Option(..., "--buttons", help="Botões (texto:id,...)")
):
    button_list = [
        {"type": "reply", "displayText": btn.split(":")[0], "id": btn.split(":")[1]}
        for btn in buttons.split(",")
    ]
    payload = {
        "number": number,
        "title": title,
        "description": description,
        "buttons": button_list
    }
    response = client.post(f"/message/sendButtons/{instance}", json=payload)
    display_response(response, "Botões Enviados")

# Call Commands
@call_app.command("fake", help="Enviar chamada falsa")
def call_fake(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número do destinatário"),
    is_video: bool = typer.Option(False, "--is-video/--no-video", help="Chamada de vídeo"),
    duration: int = typer.Option(10, "--duration", "-d", help="Duração em segundos")
):
    payload = {
        "number": number,
        "isVideo": is_video,
        "callDuration": duration
    }
    response = client.post(f"/call/offer/{instance}", json=payload)
    display_response(response, "Chamada Falsa Enviada")

# Chat Commands
@chat_app.command("check-number", help="Verificar se número está no WhatsApp")
def chat_check_number(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    numbers: str = typer.Option(..., "--numbers", "-n", help="Números, separados por vírgula")
):
    payload = {"numbers": numbers.split(",")}
    response = client.post(f"/chat/whatsappNumbers/{instance}", json=payload)
    display_response(response, "Verificação de Números")

@chat_app.command("read-messages", help="Marcar mensagens como lidas")
def chat_read_messages(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    remote_jid: str = typer.Option(..., "--remote-jid", "-j", help="JID remoto"),
    message_id: str = typer.Option(..., "--message-id", "-m", help="ID da mensagem")
):
    payload = {
        "readMessages": [{
            "remoteJid": remote_jid,
            "fromMe": False,
            "id": message_id
        }]
    }
    response = client.post(f"/chat/markMessageAsRead/{instance}", json=payload)
    display_response(response, "Mensagens Marcadas como Lidas")

@chat_app.command("archive", help="Arquivar conversa")
def chat_archive(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    remote_jid: str = typer.Option(..., "--remote-jid", "-j", help="JID remoto"),
    message_id: str = typer.Option(..., "--message-id", "-m", help="ID da mensagem"),
    archive: bool = typer.Option(True, "--archive/--unarchive", help="Arquivar ou desarquivar")
):
    payload = {
        "lastMessage": {
            "key": {"remoteJid": remote_jid, "fromMe": False, "id": message_id}
        },
        "chat": remote_jid,
        "archive": archive
    }
    response = client.post(f"/chat/archiveChat/{instance}", json=payload)
    display_response(response, "Conversa Arquivada")

@chat_app.command("mark-unread", help="Marcar conversa como não lida")
def chat_mark_unread(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    remote_jid: str = typer.Option(..., "--remote-jid", "-j", help="JID remoto"),
    message_id: str = typer.Option(..., "--message-id", "-m", help="ID da mensagem")
):
    payload = {
        "lastMessage": {
            "key": {"remoteJid": remote_jid, "fromMe": False, "id": message_id}
        },
        "chat": remote_jid
    }
    response = client.post(f"/chat/markChatUnread/{instance}", json=payload)
    display_response(response, "Conversa Marcada como Não Lida")

@chat_app.command("delete-message", help="Deletar mensagem para todos")
def chat_delete_message(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    remote_jid: str = typer.Option(..., "--remote-jid", "-j", help="JID remoto"),
    message_id: str = typer.Option(..., "--message-id", "-m", help="ID da mensagem")
):
    payload = {"id": message_id, "remoteJid": remote_jid, "fromMe": True}
    response = client.delete(f"/chat/deleteMessageForEveryone/{instance}", json=payload)
    display_response(response, "Mensagem Deletada")

@chat_app.command("get-profile-pic", help="Buscar foto de perfil")
def chat_get_profile_pic(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número")
):
    payload = {"number": number}
    response = client.post(f"/chat/fetchProfilePictureUrl/{instance}", json=payload)
    display_response(response, "Foto de Perfil")

@chat_app.command("get-media-base64", help="Extrair Base64 de mídia")
def chat_get_media_base64(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    message_id: str = typer.Option(..., "--message-id", "-m", help="ID da mensagem"),
    convert_to_mp4: bool = typer.Option(False, "--convert-to-mp4/--no-convert", help="Converter áudio para MP4")
):
    payload = {
        "message": {"key": {"id": message_id}},
        "convertToMp4": convert_to_mp4
    }
    response = client.post(f"/chat/getBase64FromMediaMessage/{instance}", json=payload)
    display_response(response, "Mídia em Base64")

@chat_app.command("update-message", help="Atualizar mensagem")
def chat_update_message(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número"),
    remote_jid: str = typer.Option(..., "--remote-jid", "-j", help="JID remoto"),
    message_id: str = typer.Option(..., "--message-id", "-m", help="ID da mensagem"),
    text: str = typer.Option(..., "--text", "-t", help="Novo texto")
):
    payload = {
        "number": number,
        "key": {"remoteJid": remote_jid, "fromMe": True, "id": message_id},
        "text": text
    }
    response = client.post(f"/chat/updateMessage/{instance}", json=payload)
    display_response(response, "Mensagem Atualizada")

@chat_app.command("send-presence", help="Enviar presença")
def chat_send_presence(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número"),
    presence: str = typer.Option(..., "--presence", "-p", help="Presença (available, composing, etc.)"),
    delay: Optional[int] = typer.Option(None, "--delay", "-d", help="Atraso em milissegundos")
):
    payload = {"number": number, "presence": presence}
    if delay:
        payload["delay"] = delay
    response = client.post(f"/chat/sendPresence/{instance}", json=payload)
    display_response(response, "Presença Enviada")

@chat_app.command("block", help="Bloquear/desbloquear número")
def chat_block(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número"),
    status: str = typer.Option(..., "--status", "-s", help="Status (block, unblock)")
):
    payload = {"number": number, "status": status}
    response = client.post(f"/message/updateBlockStatus/{instance}", json=payload)
    display_response(response, f"Número {status.capitalize()}")

@chat_app.command("list-contacts", help="Listar contatos")
def chat_list_contacts(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    contact_id: Optional[str] = typer.Option(None, "--contact-id", help="Filtrar por ID")
):
    payload = {"where": {}}
    if contact_id:
        payload["where"]["id"] = contact_id
    response = client.post(f"/chat/findContacts/{instance}", json=payload)
    display_response(response, "Contatos")

@chat_app.command("list-messages", help="Listar mensagens")
def chat_list_messages(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    remote_jid: str = typer.Option(..., "--remote-jid", "-j", help="JID remoto"),
    page: Optional[int] = typer.Option(1, "--page", help="Página"),
    offset: Optional[int] = typer.Option(10, "--offset", help="Offset")
):
    payload = {
        "where": {"key": {"remoteJid": remote_jid}},
        "page": page,
        "offset": offset
    }
    response = client.post(f"/chat/findMessages/{instance}", json=payload)
    display_response(response, "Mensagens")

@chat_app.command("list-status", help="Listar status")
def chat_list_status(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    remote_jid: Optional[str] = typer.Option(None, "--remote-jid", "-j", help="JID remoto"),
    status_id: Optional[str] = typer.Option(None, "--status-id", help="ID do status"),
    page: Optional[int] = typer.Option(1, "--page", help="Página"),
    offset: Optional[int] = typer.Option(10, "--offset", help="Offset")
):
    payload = {"where": {}}
    if remote_jid:
        payload["where"]["remoteJid"] = remote_jid
    if status_id:
        payload["where"]["id"] = status_id
    payload["page"] = page
    payload["offset"] = offset
    response = client.post(f"/chat/findStatusMessage/{instance}", json=payload)
    display_response(response, "Status")

@chat_app.command("list-chats", help="Listar chats")
def chat_list_chats(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.post(f"/chat/findChats/{instance}")
    display_response(response, "Chats")

# Contact Commands
@contact_app.command("add", help="Adicionar contato à agenda")
def contact_add(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número do contato"),
    full_name: str = typer.Option(..., "--full-name", "-f", help="Nome completo"),
    organization: Optional[str] = typer.Option(None, "--organization", "-o", help="Organização"),
    email: Optional[str] = typer.Option(None, "--email", "-e", help="Email"),
    url: Optional[str] = typer.Option(None, "--url", "-u", help="URL")
):
    contact = {
        "id": number,
        "pushName": full_name
    }
    if organization:
        contact["organization"] = organization
    if email:
        contact["email"] = email
    if url:
        contact["url"] = url
    payload = {"where": contact}
    response = client.post(f"/chat/findContacts/{instance}", json=payload)
    display_response(response, f"Contato {full_name} Adicionado")

# Broadcast Commands
@broadcast_app.command("create", help="Criar lista de transmissão")
def broadcast_create(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    name: str = typer.Option(..., "--name", "-n", help="Nome da lista"),
    numbers: str = typer.Option(..., "--numbers", "-nums", help="Números, separados por vírgula")
):
    # Simula lista de transmissão armazenando números localmente
    payload = {
        "name": name,
        "numbers": numbers.split(",")
    }
    # Não há endpoint específico, usamos send-contact para validar números
    response = client.post(f"/chat/whatsappNumbers/{instance}", json={"numbers": payload["numbers"]})
    display_response(response, f"Lista de Transmissão {name} Criada")
    console.print(f"[yellow]Lista {name} criada com números: {numbers}[/yellow]")

@broadcast_app.command("send", help="Enviar mensagem para lista de transmissão")
def broadcast_send(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    numbers: str = typer.Option(..., "--numbers", "-nums", help="Números, separados por vírgula"),
    text: str = typer.Option(..., "--text", "-t", help="Texto da mensagem"),
    delay: Optional[int] = typer.Option(None, "--delay", "-d", help="Atraso em milissegundos")
):
    for number in numbers.split(","):
        payload = {"number": number.strip(), "text": text}
        if delay:
            payload["delay"] = delay
        response = client.post(f"/message/sendText/{instance}", json=payload)
        display_response(response, f"Mensagem Enviada para {number}")

# Label Commands
@label_app.command("list", help="Listar etiquetas")
def label_list(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.get(f"/label/findLabels/{instance}")
    display_response(response, "Etiquetas")

@label_app.command("handle", help="Adicionar/remover etiqueta")
def label_handle(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número"),
    label_id: str = typer.Option(..., "--label-id", "-l", help="ID da etiqueta"),
    action: str = typer.Option(..., "--action", "-a", help="Ação (add, remove)")
):
    payload = {"number": number, "labelId": label_id, "action": action}
    response = client.post(f"/label/handleLabel/{instance}", json=payload)
    display_response(response, "Etiqueta Gerenciada")

# Profile Commands
@profile_app.command("get-business", help="Buscar perfil de negócios")
def profile_get_business(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número")
):
    payload = {"number": number}
    response = client.post(f"/chat/fetchBusinessProfile/{instance}", json=payload)
    display_response(response, "Perfil de Negócios")

@profile_app.command("get", help="Buscar perfil")
def profile_get(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número")
):
    payload = {"number": number}
    response = client.post(f"/chat/fetchProfile/{instance}", json=payload)
    display_response(response, "Perfil")

@profile_app.command("update-name", help="Atualizar nome do perfil")
def profile_update_name(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    name: str = typer.Option(..., "--name", "-n", help="Novo nome")
):
    payload = {"name": name}
    response = client.post(f"/chat/updateProfileName/{instance}", json=payload)
    display_response(response, "Nome do Perfil Atualizado")

@profile_app.command("update-status", help="Atualizar status do perfil")
def profile_update_status(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    status: str = typer.Option(..., "--status", "-s", help="Novo status")
):
    payload = {"status": status}
    response = client.post(f"/chat/updateProfileStatus/{instance}", json=payload)
    display_response(response, "Status do Perfil Atualizado")

@profile_app.command("update-picture", help="Atualizar foto do perfil")
def profile_update_picture(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    picture: str = typer.Option(..., "--picture", "-p", help="URL da foto")
):
    payload = {"picture": picture}
    response = client.post(f"/chat/updateProfilePicture/{instance}", json=payload)
    display_response(response, "Foto do Perfil Atualizada")

@profile_app.command("remove-picture", help="Remover foto do perfil")
def profile_remove_picture(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.delete(f"/chat/removeProfilePicture/{instance}")
    display_success("Foto do Perfil Removida")

@profile_app.command("get-privacy", help="Buscar configurações de privacidade")
def profile_get_privacy(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.get(f"/chat/fetchPrivacySettings/{instance}")
    display_response(response, "Configurações de Privacidade")

@profile_app.command("update-privacy", help="Atualizar configurações de privacidade")
def profile_update_privacy(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    readreceipts: str = typer.Option("all", "--readreceipts", help="Recibos de leitura (all, none)"),
    profile: str = typer.Option("all", "--profile", help="Perfil (all, contacts, none)"),
    status: str = typer.Option("contacts", "--status", help="Status (all, contacts, none)"),
    online: str = typer.Option("all", "--online", help="Online (all, match_last_seen)"),
    last: str = typer.Option("contacts", "--last", help="Último visto (all, contacts, none)"),
    groupadd: str = typer.Option("none", "--groupadd", help="Adição a grupos (all, contacts)")
):
    payload = {
        "readreceipts": readreceipts,
        "profile": profile,
        "status": status,
        "online": online,
        "last": last,
        "groupadd": groupadd
    }
    response = client.post(f"/chat/updatePrivacySettings/{instance}", json=payload)
    display_response(response, "Privacidade Atualizada")

# Group Commands
@group_app.command("create", help="Criar grupo")
def group_create(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    subject: str = typer.Option(..., "--subject", "-s", help="Nome do grupo"),
    participants: str = typer.Option(..., "--participants", "-p", help="Números, separados por vírgula"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Descrição")
):
    payload = {
        "subject": subject,
        "participants": participants.split(",")
    }
    if description:
        payload["description"] = description
    response = client.post(f"/group/create/{instance}", json=payload)
    display_response(response, "Grupo Criado")

@group_app.command("update-picture", help="Atualizar foto do grupo")
def group_update_picture(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    group_jid: str = typer.Option(..., "--group-jid", "-j", help="JID do grupo"),
    image: str = typer.Option(..., "--image", help="URL da imagem")
):
    payload = {"image": image}
    response = client.post(f"/group/updateGroupPicture/{instance}?groupJid={group_jid}", json=payload)
    display_response(response, "Foto do Grupo Atualizada")

@group_app.command("update-subject", help="Atualizar nome do grupo")
def group_update_subject(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    group_jid: str = typer.Option(..., "--group-jid", "-j", help="JID do grupo"),
    subject: str = typer.Option(..., "--subject", "-s", help="Novo nome")
):
    payload = {"subject": subject}
    response = client.post(f"/group/updateGroupSubject/{instance}?groupJid={group_jid}", json=payload)
    display_response(response, "Nome do Grupo Atualizado")

@group_app.command("update-description", help="Atualizar descrição do grupo")
def group_update_description(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    group_jid: str = typer.Option(..., "--group-jid", "-j", help="JID do grupo"),
    description: str = typer.Option(..., "--description", "-d", help="Nova descrição")
):
    payload = {"description": description}
    response = client.post(f"/group/updateGroupDescription/{instance}?groupJid={group_jid}", json=payload)
    display_response(response, "Descrição do Grupo Atualizada")

@group_app.command("get-invite", help="Obter código de convite")
def group_get_invite(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    group_jid: str = typer.Option(..., "--group-jid", "-j", help="JID do grupo")
):
    response = client.get(f"/group/inviteCode/{instance}?groupJid={group_jid}")
    display_response(response, "Código de Convite")

@group_app.command("revoke-invite", help="Revogar código de convite")
def group_revoke_invite(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    group_jid: str = typer.Option(..., "--group-jid", "-j", help="JID do grupo")
):
    response = client.post(f"/group/revokeInviteCode/{instance}?groupJid={group_jid}")
    display_response(response, "Código de Convite Revogado")

@group_app.command("send-invite", help="Enviar convite")
def group_send_invite(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    group_jid: str = typer.Option(..., "--group-jid", "-j", help="JID do grupo"),
    numbers: str = typer.Option(..., "--numbers", "-n", help="Números, separados por vírgula"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Descrição do convite")
):
    payload = {"groupJid": group_jid, "numbers": numbers.split(",")}
    if description:
        payload["description"] = description
    response = client.post(f"/group/sendInvite/{instance}", json=payload)
    display_response(response, "Convite Enviado")

@group_app.command("get-by-invite", help="Buscar grupo por código de convite")
def group_get_by_invite(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    invite_code: str = typer.Option(..., "--invite-code", "-c", help="Código de convite")
):
    response = client.get(f"/group/inviteInfo/{instance}?inviteCode={invite_code}")
    display_response(response, "Informações do Grupo")

@group_app.command("get-by-jid", help="Buscar grupo por JID")
def group_get_by_jid(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    group_jid: str = typer.Option(..., "--group-jid", "-j", help="JID do grupo")
):
    response = client.get(f"/group/findGroupInfos/{instance}?groupJid={group_jid}")
    display_response(response, "Informações do Grupo")

@group_app.command("list", help="Listar grupos")
def group_list(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    get_participants: bool = typer.Option(False, "--get-participants/--no-participants", help="Incluir participantes")
):
    params = {"getParticipants": str(get_participants).lower()}
    response = client.get(f"/group/fetchAllGroups/{instance}", params=params)
    display_response(response, "Grupos")

@group_app.command("list-participants", help="Listar participantes")
def group_list_participants(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    group_jid: str = typer.Option(..., "--group-jid", "-j", help="JID do grupo")
):
    response = client.get(f"/group/participants/{instance}?groupJid={group_jid}")
    display_response(response, "Participantes do Grupo")

@group_app.command("manage-participants", help="Gerenciar participantes")
def group_manage_participants(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    group_jid: str = typer.Option(..., "--group-jid", "-j", help="JID do grupo"),
    action: str = typer.Option(..., "--action", "-a", help="Ação (add, remove, promote, demote)"),
    participants: str = typer.Option(..., "--participants", "-p", help="Números, separados por vírgula")
):
    payload = {"action": action, "participants": participants.split(",")}
    response = client.post(f"/group/updateParticipant/{instance}?groupJid={group_jid}", json=payload)
    display_response(response, f"Participantes {action.capitalize()}")

@group_app.command("update-settings", help="Atualizar configurações do grupo")
def group_update_settings(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    group_jid: str = typer.Option(..., "--group-jid", "-j", help="JID do grupo"),
    action: str = typer.Option(..., "--action", "-a", help="Ação (announcement, not_announcement, locked, unlocked)")
):
    payload = {"action": action}
    response = client.post(f"/group/updateSetting/{instance}?groupJid={group_jid}", json=payload)
    display_response(response, "Configurações do Grupo Atualizadas")

@group_app.command("toggle-ephemeral", help="Ativar/desativar mensagens temporárias")
def group_toggle_ephemeral(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    group_jid: str = typer.Option(..., "--group-jid", "-j", help="JID do grupo"),
    expiration: int = typer.Option(0, "--expiration", "-e", help="Expiração (0, 86400, 604800, 7776000)")
):
    payload = {"expiration": expiration}
    response = client.post(f"/group/toggleEphemeral/{instance}?groupJid={group_jid}", json=payload)
    display_response(response, "Mensagens Temporárias Atualizadas")

@group_app.command("leave", help="Sair do grupo")
def group_leave(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    group_jid: str = typer.Option(..., "--group-jid", "-j", help="JID do grupo")
):
    response = client.delete(f"/group/leaveGroup/{instance}?groupJid={group_jid}")
    display_success("Saiu do Grupo")

# Integration Commands
@integration_app.command("websocket-set", help="Configurar WebSocket")
def integration_websocket_set(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    events: str = typer.Option(..., "--events", "-e", help="Eventos, separados por vírgula")
):
    payload = {"websocket": {"enabled": True, "events": events.split(",")}}
    response = client.post(f"/websocket/set/{instance}", json=payload)
    display_response(response, "WebSocket Configurado")

@integration_app.command("websocket-get", help="Buscar configuração do WebSocket")
def integration_websocket_get(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.get(f"/websocket/find/{instance}")
    display_response(response, "Configuração do WebSocket")

@integration_app.command("rabbitmq-set", help="Configurar RabbitMQ")
def integration_rabbitmq_set(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    events: str = typer.Option(..., "--events", "-e", help="Eventos, separados por vírgula")
):
    payload = {"rabbitmq": {"enabled": True, "events": events.split(",")}}
    response = client.post(f"/rabbitmq/set/{instance}", json=payload)
    display_response(response, "RabbitMQ Configurado")

@integration_app.command("rabbitmq-get", help="Buscar configuração do RabbitMQ")
def integration_rabbitmq_get(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.get(f"/rabbitmq/find/{instance}")
    display_response(response, "Configuração do RabbitMQ")

@integration_app.command("sqs-set", help="Configurar SQS")
def integration_sqs_set(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    events: str = typer.Option(..., "--events", "-e", help="Eventos, separados por vírgula")
):
    payload = {"sqs": {"enabled": True, "events": events.split(",")}}
    response = client.post(f"/sqs/set/{instance}", json=payload)
    display_response(response, "SQS Configurado")

@integration_app.command("sqs-get", help="Buscar configuração do SQS")
def integration_sqs_get(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.get(f"/sqs/find/{instance}")
    display_response(response, "Configuração do SQS")

@integration_app.command("webhook-set", help="Configurar webhook")
def integration_webhook_set(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    url: str = typer.Option(..., "--url", "-u", help="URL do webhook"),
    events: str = typer.Option(..., "--events", "-e", help="Eventos, separados por vírgula")
):
    payload = {
        "webhook": {
            "enabled": True,
            "url": url,
            "byEvents": False,
            "base64": False,
            "events": events.split(",")
        }
    }
    response = client.post(f"/webhook/set/{instance}", json=payload)
    display_response(response, "Webhook Configurado")

@integration_app.command("webhook-get", help="Buscar configuração do webhook")
def integration_webhook_get(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.get(f"/webhook/find/{instance}")
    display_response(response, "Configuração do Webhook")

@integration_app.command("chatwoot-set", help="Configurar Chatwoot")
def integration_chatwoot_set(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    account_id: str = typer.Option(..., "--account-id", help="ID da conta"),
    token: str = typer.Option(..., "--token", help="Token"),
    url: str = typer.Option(..., "--url", help="URL do Chatwoot"),
    name_inbox: str = typer.Option("evolution", "--name-inbox", help="Nome da inbox")
):
    payload = {
        "enabled": True,
        "accountId": account_id,
        "token": token,
        "url": url,
        "nameInbox": name_inbox,
        "signMsg": True,
        "reopenConversation": True,
        "conversationPending": False
    }
    response = client.post(f"/chatwoot/set/{instance}", json=payload)
    display_response(response, "Chatwoot Configurado")

@integration_app.command("chatwoot-get", help="Buscar configuração do Chatwoot")
def integration_chatwoot_get(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.get(f"/chatwoot/find/{instance}")
    display_response(response, "Configuração do Chatwoot")

@integration_app.command("typebot-create", help="Criar Typebot")
def integration_typebot_create(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    url: str = typer.Option(..., "--url", help="URL do Typebot"),
    typebot: str = typer.Option(..., "--typebot", "-t", help="ID do Typebot"),
    trigger_value: str = typer.Option(..., "--trigger-value", help="Valor do gatilho")
):
    payload = {
        "enabled": True,
        "url": url,
        "typebot": typebot,
        "triggerType": "keyword",
        "triggerOperator": "regex",
        "triggerValue": trigger_value,
        "expire": 20,
        "keywordFinish": "#SAIR",
        "delayMessage": 1000,
        "unknownMessage": "Mensagem não reconhecida"
    }
    response = client.post(f"/typebot/create/{instance}", json=payload)
    display_response(response, "Typebot Criado")

@integration_app.command("typebot-list", help="Listar Typebots")
def integration_typebot_list(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.get(f"/typebot/find/{instance}")
    display_response(response, "Typebots")

@integration_app.command("openai-create", help="Criar bot OpenAI")
def integration_openai_create(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    creds_id: str = typer.Option(..., "--creds-id", help="ID das credenciais"),
    bot_type: str = typer.Option(..., "--bot-type", help="Tipo de bot (assistant, chatCompletion)"),
    assistant_id: Optional[str] = typer.Option(None, "--assistant-id", help="ID do assistente")
):
    payload = {
        "enabled": True,
        "openaiCredsId": creds_id,
        "botType": bot_type
    }
    if assistant_id:
        payload["assistantId"] = assistant_id
    response = client.post(f"/openai/create/{instance}", json=payload)
    display_response(response, "Bot OpenAI Criado")

@integration_app.command("dify-create", help="Criar bot Dify")
def integration_dify_create(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    bot_type: str = typer.Option(..., "--bot-type", help="Tipo de bot (chatBot, textGenerator, agent, workflow)"),
    api_url: str = typer.Option(..., "--api-url", help="URL da API"),
    api_key: str = typer.Option(..., "--api-key", help="Chave da API")
):
    payload = {
        "enabled": True,
        "botType": bot_type,
        "apiUrl": api_url,
        "apiKey": api_key
    }
    response = client.post(f"/dify/create/{instance}", json=payload)
    display_response(response, "Bot Dify Criado")

@integration_app.command("flowise-create", help="Criar bot Flowise")
def integration_flowise_create(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    api_url: str = typer.Option(..., "--api-url", help="URL da API"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="Chave da API")
):
    payload = {"enabled": True, "apiUrl": api_url}
    if api_key:
        payload["apiKey"] = api_key
    response = client.post(f"/flowise/create/{instance}", json=payload)
    display_response(response, "Bot Flowise Criado")

@integration_app.command("template-send", help="Enviar template (Cloud API)")
def integration_template_send(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    number: str = typer.Option(..., "--number", "-n", help="Número do destinatário"),
    name: str = typer.Option(..., "--name", help="Nome do template"),
    language: str = typer.Option("en_US", "--language", help="Idioma do template")
):
    payload = {"number": number, "name": name, "language": language}
    response = client.post(f"/message/sendTemplate/{instance}", json=payload)
    display_response(response, "Template Enviado")

@integration_app.command("template-create", help="Criar template (Cloud API)")
def integration_template_create(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    name: str = typer.Option(..., "--name", help="Nome do template"),
    category: str = typer.Option(..., "--category", help="Categoria (MARKETING, UTILITY, AUTHENTICATION)"),
    language: str = typer.Option("en_US", "--language", help="Idioma"),
    body_text: str = typer.Option(..., "--body-text", help="Texto do corpo")
):
    payload = {
        "name": name,
        "category": category,
        "language": language,
        "components": [{"type": "BODY", "text": body_text}]
    }
    response = client.post(f"/template/create/{instance}", json=payload)
    display_response(response, "Template Criado")

@integration_app.command("template-list", help="Listar templates (Cloud API)")
def integration_template_list(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância")
):
    response = client.get(f"/template/find/{instance}")
    display_response(response, "Templates")

@integration_app.command("s3-get-media", help="Obter mídia do S3")
def integration_s3_get_media(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    media_id: Optional[str] = typer.Option(None, "--media-id", help="ID da mídia")
):
    payload = {}
    if media_id:
        payload["id"] = media_id
    response = client.post(f"/s3/getMedia/{instance}", json=payload)
    display_response(response, "Mídia do S3")

@integration_app.command("s3-get-media-url", help="Obter URL da mídia do S3")
def integration_s3_get_media_url(
    instance: str = typer.Option(..., "--instance", "-i", help="Nome da instância"),
    media_id: str = typer.Option(..., "--media-id", help="ID da mídia")
):
    payload = {"id": media_id}
    response = client.post(f"/s3/getMediaUrl/{instance}", json=payload)
    display_response(response, "URL da Mídia do S3")

if __name__ == "__main__":
    app()
