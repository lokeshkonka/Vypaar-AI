
import {
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/clerk-react";

export default function Navbar() {

  return (
    <header className="dashboard-header">
      <h2>Vyapaar AI</h2>

      <SignedIn>
        <UserButton />
      </SignedIn>

      <SignedOut>{/* no UI */}</SignedOut>
    </header>
  );
}
