import Stack from 'react-bootstrap/Stack';
import Image from 'react-bootstrap/Image';
import { Link } from 'react-router-dom';

export default function Post({ post }) {
  return (
    <Stack direction="horizontal" gap={3} className="Post">
      <Image src={post.avatar}
        alt={post.name} roundedCircle />
      <div>
        <p>
          <Link to={'/accountants/' + post.username}>
            {post.name}
          </Link>
          &nbsp;&mdash;&nbsp;
          {post.email}:
        </p>
        <p>{post.about_me}</p>
      </div>
    </Stack>
  );
}