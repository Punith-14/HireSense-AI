import { Brain, BriefcaseBusiness, CheckCircle2, Users } from "lucide-react";

export const agents = [
  {
    id: "technical",
    title: "Technical Agent",
    description: "DSA, coding, backend, OOPs, system design",
    icon: Brain,
  },
  {
    id: "hr",
    title: "HR Agent",
    description: "Communication, confidence, personality",
    icon: BriefcaseBusiness,
  },
  {
    id: "behavioral",
    title: "Behavioral Agent",
    description: "Leadership, teamwork, decision making",
    icon: Users,
  },
];

export default function AgentSelector({ selectedAgent, onSelect }) {
  return (
    <div className="card-grid three">
      {agents.map((agent) => {
        const Icon = agent.icon;
        const selected = selectedAgent === agent.id;

        return (
          <button
            className={`selectable ${selected ? "selected" : ""}`}
            key={agent.id}
            onClick={() => onSelect(agent.id)}
            type="button"
          >
            <div className="agent-icon">
              <Icon size={22} />
            </div>
            <strong>{agent.title}</strong>
            <span className="desc">{agent.description}</span>
            <span className="sel-label">
              {selected && <CheckCircle2 size={13} />}
              {selected ? "Selected" : "Select agent"}
            </span>
          </button>
        );
      })}
    </div>
  );
}
