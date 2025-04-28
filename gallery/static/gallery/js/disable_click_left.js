function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.showModal();
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.close();
}

document.addEventListener('contextmenu', e => e.preventDefault());
    document.addEventListener('keydown', e => {
         if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && e.key === 'I')) {
            e.preventDefault();
        }
    });