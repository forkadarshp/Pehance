import { CentralPrompt } from "@/components/organisms/CentralPrompt";
import { Footer } from "@/components/organisms/Footer";
import { Header } from "@/components/organisms/Header";
import { Container } from "@mantine/core";

export default function Home() {
  return (
    <Container 
      size="xl" 
      style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        flexDirection: 'column',
        position: 'relative',
        padding: 0,
      }}
    >
      <Header />

      {/* Main content */}
      <main style={{ flex: 1, zIndex: 10 }}>
        <CentralPrompt />
      </main>
      
      {/* Footer */}
      <div style={{ zIndex: 10, padding: '2rem' }}>
        <Footer />
      </div>
    </Container>
  );
}
