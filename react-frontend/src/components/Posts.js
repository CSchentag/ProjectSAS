import { useState, useEffect } from 'react';
import Spinner from 'react-bootstrap/Spinner';
import { useApi } from '../contexts/ApiProvider';
import Post from './Post';

export default function Posts() {
  const [posts, setPosts] = useState();
  const api = useApi();

  useEffect(() => {
    (async () => {
      const response = await api.get('/accountants/');
      if (response.ok) {
        setPosts(response.body.data);
      }
      else {
        setPosts(null);
      }
    })();
  }, [api]);

  return (
    <>
      {posts === undefined ?
        <Spinner animation="border" />
      :
        <>
          {posts === null ?
             <p>Could not retrieve accountant data.</p>
          :
            <>
              {posts.length === 0 ?
                <p>No accountants found in database.</p>
              :
                posts.map(post => <Post key={post.id} post={post} />)
              }
            </>
          }
        </>
      }
    </>
  );
}