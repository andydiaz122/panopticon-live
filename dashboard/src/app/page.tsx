import PanopticonEngine from '@/components/PanopticonEngine';

export default function Home() {
  return (
    <main
      style={{
        minHeight: '100vh',
        width: '100%',
        background: '#0A0A0A',
        color: '#fff',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 24,
      }}
    >
      <div
        style={{
          width: 'min(100%, 1280px)',
          aspectRatio: '16 / 9',
          position: 'relative',
          boxShadow: '0 0 40px rgba(0, 255, 255, 0.15)',
        }}
      >
        <PanopticonEngine
          videoSrc="/clips/utr_match_01_segment_a.mp4"
          matchDataSrc="/match_data/utr_01_segment_a.json"
        />
      </div>
    </main>
  );
}
