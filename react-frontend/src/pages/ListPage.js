import Body from '../components/Body';
import Accountants from '../components/Accountants';

export default function ListPage() {
  return (
    <Body sidebar>
      <br/>
      <h5>This is a list of all accountants currently in the database.</h5>
      <br/>
      <Accountants />
    </Body>
  );
}