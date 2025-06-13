import { useState, useEffect, useRef } from 'react';
import { 
  IconBuilding, 
} from '@tabler/icons-react';
import styles from './Home.module.scss';

export const Home = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isLoaded, setIsLoaded] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setMousePosition({
          x: ((e.clientX - rect.left) / rect.width - 0.5) * 100,
          y: ((e.clientY - rect.top) / rect.height - 0.5) * 100
        });
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    setTimeout(() => setIsLoaded(true), 500);

    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const buildings = [
    { height: '8rem', delay: 0, services: ['Отопление', 'Водоснабжение'] },
    { height: '10rem', delay: 200, services: ['Электричество', 'Интернет'] },
    { height: '7rem', delay: 400, services: ['Газ', 'Уборка'] },
    { height: '9rem', delay: 600, services: ['Охрана', 'Паркинг'] },
    { height: '11rem', delay: 800, services: ['Лифт', 'Вентиляция'] },
    { height: '8rem', delay: 1000, services: ['ТВ', 'Домофон'] }
  ];

  return (
    <>
      <div 
        ref={containerRef}
        className={styles.container}
        style={{
          background: `radial-gradient(circle at ${50 + mousePosition.x * 0.1}% ${50 + mousePosition.y * 0.1}%, 
            rgba(99, 102, 241, 0.3) 0%, 
            rgba(168, 85, 247, 0.2) 35%, 
            rgba(236, 72, 153, 0.1) 100%)`
        }}
      >
        <div className={styles.gridBackground}>
          <div 
            className={styles.grid}
            style={{
              transform: `translate(${mousePosition.x * 0.1}px, ${mousePosition.y * 0.1}px)`
            }}
          />
        </div>

        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className={styles.particle}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDuration: `${3 + Math.random() * 4}s`,
              animationDelay: `${Math.random() * 2}s`
            }}
          />
        ))}

        <div className={styles.mainContent}>
          
          <div className={`${styles.header} ${isLoaded ? styles.loaded : ''}`}>
            <div className={styles.logoContainer}>
              <div 
                className={styles.logo}
                style={{
                  transform: `perspective(1000px) rotateX(${mousePosition.y * 0.1}deg) rotateY(${mousePosition.x * 0.1}deg)`
                }}
              >
                <IconBuilding size={80} className={styles.logoIcon} />
                <div className={styles.logoShine} />
                
                <div className={styles.holoRing1} />
                <div className={styles.holoRing2} />
              </div>
              
              {[...Array(8)].map((_, i) => (
                <div
                  key={i}
                  className={styles.energyDot}
                  style={{
                    top: `${50 + Math.sin((Date.now() * 0.001) + i) * 40}%`,
                    left: `${50 + Math.cos((Date.now() * 0.001) + i) * 40}%`,
                    animationDelay: `${i * 0.5}s`
                  }}
                />
              ))}
            </div>

            <h1 className={styles.mainTitle}>SMART</h1>
            <h2 className={styles.subTitle}>ЖКХ</h2>
            
            <div className={styles.titleDivider}>
              <div className={styles.dividerLine} />
              <span className={styles.dividerText}>FUTURE OF UTILITIES</span>
              <div className={styles.dividerLine} />
            </div>
          </div>

          <div className={`${styles.cityContainer} ${isLoaded ? styles.loaded : ''}`}>
            <div className={styles.buildings}>
              {buildings.map((building, index) => (
                <div
                  key={index}
                  className={styles.building}
                  style={{
                    height: building.height,
                    animationDelay: `${building.delay}ms`,
                    transform: `perspective(500px) rotateX(${mousePosition.y * 0.05}deg) rotateY(${mousePosition.x * 0.05}deg)`
                  }}
                >
                  <div className={styles.windows}>
                    {[...Array(8)].map((_, i) => (
                      <div
                        key={i}
                        className={`${styles.window} ${Math.random() > 0.3 ? styles.lit : ''}`}
                        style={{
                          animationDelay: `${Math.random() * 2}s`
                        }}
                      />
                    ))}
                  </div>
                  
                  <div className={styles.antenna} />
                  <div className={styles.antennaLight} />
                  
                  <div className={styles.tooltip}>
                    <div className={styles.tooltipContent}>
                      {building.services.join(' • ')}
                      <div className={styles.tooltipArrow} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className={styles.groundReflection} />
          </div>
        </div>
      </div>
    </>
  );
};
