import { Badge } from "@/components/atoms/Badge";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/atoms/Card";
import { Container, Grid, Title } from "@mantine/core";

const dashboardData = [
  {
    title: "Total Prompts Enhanced",
    value: "1,250",
    change: "+15.2%",
    changeType: "increase",
  },
  {
    title: "Average Confidence Score",
    value: "88.5%",
    change: "+2.1%",
    changeType: "increase",
  },
  {
    title: "Most Common Intent",
    value: "Technical",
    change: "Web Development",
    changeType: "neutral",
  },
  {
    title: "API Usage (Last 24h)",
    value: "4,821 calls",
    change: "-5.8%",
    changeType: "decrease",
  },
];

export default function DashboardPage() {
  return (
    <Container size="xl" p="xl">
      <Title order={1} mb="xl">Analytics Dashboard</Title>
      <Grid>
        {dashboardData.map((item, index) => (
          <Grid.Col key={index} span={{ base: 12, sm: 6, lg: 3 }}>
            <Card>
              <CardHeader>
                <CardTitle>{item.title}</CardTitle>
                <CardDescription>{item.value}</CardDescription>
              </CardHeader>
              <CardContent>
                <Badge
                  variant={
                    item.changeType === "increase"
                      ? "default"
                      : item.changeType === "decrease"
                      ? "destructive"
                      : "secondary"
                  }
                >
                  {item.change}
                </Badge>
              </CardContent>
            </Card>
          </Grid.Col>
        ))}
      </Grid>
    </Container>
  );
} 