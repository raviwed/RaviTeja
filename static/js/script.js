function showModal() {
    document.getElementById('modal').style.display = 'block';
}
function hideModal() {
    document.getElementById('modal').style.display = 'none';
}
function addStudent() {
    const name = document.getElementById('name').value;
    const subject = document.getElementById('subject').value;
    const marks = document.getElementById('marks').value;

    fetch('/add_student', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, subject, marks })
    }).then(() => location.reload());
}
function deleteStudent(id) {
    fetch('/delete_student/' + id, { method: 'POST' }).then(() => location.reload());
}
function saveEdit(id) {
    const row = document.querySelector(`tr[data-id='${id}']`);
    const name = row.children[0].innerText;
    const subject = row.children[1].innerText;
    const marks = row.children[2].innerText;

    fetch('/edit_student/' + id, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, subject, marks })
    }).then(() => alert('Updated successfully'));
}
