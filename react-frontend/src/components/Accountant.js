import Stack from 'react-bootstrap/Stack';
import Image from 'react-bootstrap/Image';
import { Link } from 'react-router-dom';

export default function Accountant({ accountant }) {
  return (
    <Stack direction="horizontal" gap={3} className="Accountant">
      <Image src={accountant.avatar}
        alt={accountant.name} roundedCircle />
      <div>
        <p>
          <Link to={'/accountants/' + accountant.username}>
            {accountant.name}
          </Link>
          &nbsp;&mdash;&nbsp;
          {accountant.email}:
        </p>
        <p>{accountant.about_me}</p>
      </div>
    </Stack>
  );
}