let scriptToDelete = '';  // Variável para armazenar o script a ser excluído

// Função para buscar o status dos scripts
function fetchStatus() {
    fetch('/status')
        .then(response => response.json())
        .then(data => updateTable(data))
        .catch(error => console.error('Erro ao buscar status:', error));
}

// Função para atualizar a tabela de scripts
function updateTable(scripts) {
    const tableBody = document.querySelector('#script-table tbody');
    tableBody.innerHTML = '';  // Limpa a tabela existente

    Object.keys(scripts).forEach(script_name => {
        const script_data = scripts[script_name];
        const status = script_data.process ? 'Executando' : 'Parado';
        const icon = script_data.icon ? `<img src="/icons/${script_data.icon}" class="icon-img">` : 'N/A';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${icon}</td>
            <td>${script_name}</td>
            <td>${script_data.real_name}</td>
            <td id="status-${script_name}">${status}</td>
            <td>
                <button class="btn" onclick="startScript('${script_name}')">Iniciar</button>
                <button class="btn btn-danger" onclick="stopScript('${script_name}')">Parar</button>
                <button class="btn-delete" onclick="openDeleteModal('${script_name}')">Excluir</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// Função para abrir o modal de confirmação de exclusão
function openDeleteModal(script_name) {
    scriptToDelete = script_name;
    document.getElementById('scriptToDelete').textContent = script_name;

    // Apenas exibe o modal se um script foi realmente selecionado
    if (script_name) {
        document.getElementById('confirmModal').style.display = 'flex';
    }
}

// Função para confirmar a exclusão do script
function confirmDelete() {
    if (scriptToDelete) {  // Certifique-se de que existe um script a ser excluído
        fetch('/delete', { method: 'POST', body: new URLSearchParams({ script_name: scriptToDelete }) })
            .then(response => response.json())
            .then(data => {
                showNotification(data.message || data.error);
                fetchStatus();  // Atualiza a tabela após a exclusão
                closeModal();  // Fecha o modal de confirmação
            });
    }
}

// Função para fechar o modal de exclusão
function closeModal() {
    document.getElementById('confirmModal').style.display = 'none';
}

// Função para mostrar notificações
function showNotification(message) {
    if (message) {  // Exibe notificação somente se houver mensagem válida
        document.getElementById('notificationMessage').textContent = message;
        document.getElementById('notificationModal').style.display = 'flex';
    }
}

// Função para fechar a notificação
function closeNotification() {
    document.getElementById('notificationModal').style.display = 'none';
}

// Verifica se a página acabou de carregar
window.onload = function() {
    // Garante que os modais estão fechados ao carregar a página
    closeModal();  // Fecha o modal de exclusão
    closeNotification();  // Fecha o modal de notificação
}

// Atualiza o status a cada 5 segundos
setInterval(fetchStatus, 5000);
fetchStatus();  // Chama fetchStatus assim que a página carrega

// Event listener para o upload de scripts
document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    fetch('/upload', { method: 'POST', body: formData })
        .then(response => response.json())
        .then(data => {
            showNotification(data.message || data.error);
            fetchStatus();  // Atualiza a tabela após o upload
        });
});

const fileInput = document.getElementById('script_file');
const iconInput = document.getElementById('script_icon');
const fileUploadText = document.querySelectorAll('.file-upload-text');
const fileUploadButton = document.querySelectorAll('.file-upload-button');

fileUploadButton[0].addEventListener('click', () => iconInput.click());
fileUploadButton[1].addEventListener('click', () => fileInput.click());

iconInput.addEventListener('change', function() {
    fileUploadText[0].textContent = iconInput.files[0] ? iconInput.files[0].name : 'Nenhum ícone escolhido';
});

fileInput.addEventListener('change', function() {
    fileUploadText[1].textContent = fileInput.files[0] ? fileInput.files[0].name : 'Nenhum arquivo escolhido';
});

function startScript(script_name) {
    fetch('/start', { method: 'POST', body: new URLSearchParams({ script_name }) })
        .then(response => response.json())
        .then(data => {
            showNotification(data.message || data.error);
            document.getElementById(`status-${script_name}`).textContent = 'Executando';  // Atualiza o status na tabela
            fetchStatus();  // Atualiza a tabela após iniciar o script
        });
}

function stopScript(script_name) {
    fetch('/stop', { method: 'POST', body: new URLSearchParams({ script_name }) })
        .then(response => response.json())
        .then(data => {
            showNotification(data.message || data.error);
            document.getElementById(`status-${script_name}`).textContent = 'Parado';  // Atualiza o status na tabela
            fetchStatus();  // Atualiza a tabela após parar o script
        });
}
