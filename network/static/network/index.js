
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

const editData = (id) =>
{
    var postBox = document.querySelector(`#post-${id}`)
    var editBox = document.querySelector(`#edit-box-${id}`);
    var editBtn = document.querySelector(`#edit-btn-${id}`);
    var postBody = editBox.value;
    var url = ('/' + id);

    var request = new Request(
        url,
        {headers: {'X-CSRFToken': csrftoken}}
    );

    fetch(request,
    {
        method: 'POST',
        body: JSON.stringify({ postBody: postBody })
    })

    postBox.innerHTML = postBody;
    editBox.style.display = 'none';
    editBtn.style.display = 'none';
};

function edit(id)
{
    var postBox = document.querySelector(`#post-${id}`)
    var editBox = document.querySelector(`#edit-box-${id}`);
    var editBtn = document.querySelector(`#edit-btn-${id}`);

    editBox.style.display = 'block';
    editBtn.style.display = 'block';

    editBox.innerHTML = postBox.innerHTML;
}


function like(id)
{
    var likeBtn = document.querySelector(`#like-btn-${id}`);
    var url = ('/' + id);

    var request = new Request(
        url,
        {headers: {'X-CSRFToken': csrftoken}}
    );

    fetch(request,
    {
        method: 'POST',
        body: JSON.stringify({ toggleLike: true })
    })
        .then(response => response.json())
            .then(post => { likeBtn.value = post.likes; });

    if (likeBtn.className == "btn btn-dark btn-sm ml-sm-5 mr-sm-5") likeBtn.className = "btn-sm btn btn-light btn-outline-dark ml-sm-5 mr-sm-5";
    else likeBtn.className = "btn btn-dark btn-sm ml-sm-5 mr-sm-5";

}