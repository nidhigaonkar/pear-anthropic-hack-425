document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const textarea = document.querySelector('textarea');

    // Create a container for subreddit results
    let subredditList = document.createElement('ul');
    subredditList.id = 'subreddit-list';
    subredditList.style.listStyle = 'none';
    subredditList.style.padding = '0';
    document.querySelector('.container').appendChild(subredditList);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const userInput = textarea.value.trim();

        if (userInput) {
            // First, save the description
            try {
                const submitResponse = await fetch('http://127.0.0.1:5000/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ description: userInput })
                });
                const submitResult = await submitResponse.json();
                if (!submitResponse.ok || !submitResult.success) {
                    alert(submitResult.message || 'Error saving your submission.');
                    return;
                }
            } catch (error) {
                alert('Failed to submit. Please try again later.');
                return;
            }

            // Then, get relevant subreddits
            try {
                // Clear previous results
                subredditList.innerHTML = '';
                const subResponse = await fetch('http://127.0.0.1:5000/find_subreddits', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ description: userInput })
                });
                const subResult = await subResponse.json();
                if (subResponse.ok && subResult.success) {
                    textarea.value = '';
                    if (subResult.subreddits && subResult.subreddits.length > 0) {
                        subResult.subreddits.forEach(sub => {
                            const li = document.createElement('li');
                            li.style.marginBottom = '10px';
                            
                            const link = document.createElement('a');
                            // Remove any existing r/ prefix and add it back
                            const subName = sub.replace(/^r\//, '');
                            link.href = `https://reddit.com/r/${subName}`;
                            link.target = '_blank';
                            link.textContent = sub;
                            link.style.color = '#10a37f';
                            link.style.textDecoration = 'none';
                            link.style.fontWeight = '500';
                            
                            link.addEventListener('mouseover', () => {
                                link.style.textDecoration = 'underline';
                            });
                            
                            link.addEventListener('mouseout', () => {
                                link.style.textDecoration = 'none';
                            });
                            
                            li.appendChild(link);
                            subredditList.appendChild(li);
                        });
                    } else {
                        subredditList.innerHTML = '<li>No subreddits found.</li>';
                    }
                } else {
                    alert(subResult.message || 'Error finding subreddits.');
                }
            } catch (error) {
                alert('Failed to get subreddits. Please try again later.');
            }
        } else {
            alert('Please enter a description before submitting.');
        }
    });
});
