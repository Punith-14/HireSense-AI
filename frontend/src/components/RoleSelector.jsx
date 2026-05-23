const roles = [
  "Java Developer",
  "Python Developer",
  "Frontend Developer",
  "Backend Developer",
  "AI/ML Engineer",
  "Full Stack Developer",
];

export default function RoleSelector({ selectedRole, onSelect }) {
  return (
    <div className="role-grid">
      {roles.map((role) => (
        <button
          className={`role-chip ${selectedRole === role ? "selected" : ""}`}
          key={role}
          onClick={() => onSelect(role)}
          type="button"
        >
          <span className="role-dot" />
          {role}
        </button>
      ))}
    </div>
  );
}
