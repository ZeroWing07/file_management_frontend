import React, { useRef, useState, useEffect } from 'react';

const CanvasComponent = React.forwardRef((props, ref) => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [context, setContext] = useState(null);
  const [lastPosition, setLastPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');

      // Set up canvas properties
      ctx.lineWidth = 2;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.strokeStyle = '#000000';

      // Fill with white background
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      setContext(ctx);
    }
  }, []);

  const getMousePos = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const scaleX = canvasRef.current.width / rect.width;
    const scaleY = canvasRef.current.height / rect.height;

    return {
      x: (e.clientX - rect.left) / scaleX,
      y: (e.clientY - rect.top) / scaleY
    };
  };

  const startDrawing = (e) => {
    const pos = getMousePos(e);
    setLastPosition(pos);
    setIsDrawing(true);

    // Start a new path and move to initial position
    context.beginPath();
    context.moveTo(pos.x, pos.y);
  };

  const draw = (e) => {
    if (!isDrawing) return;

    const pos = getMousePos(e);

    // Draw a line from last position to current position
    context.beginPath();
    context.moveTo(lastPosition.x, lastPosition.y);
    context.lineTo(pos.x, pos.y);
    context.stroke();

    setLastPosition(pos);
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    context.fillStyle = '#FFFFFF';
    context.fillRect(0, 0, canvas.width, canvas.height);
  };

  // Expose canvas ref and clearCanvas method to parent component
  React.useImperativeHandle(ref, () => ({
    toDataURL: () => canvasRef.current.toDataURL('image/png'),
    clearCanvas,
  }));

  return (
    <div style={{ touchAction: 'none' }}>
      <canvas
        ref={canvasRef}
        width={props.width || 200}
        height={props.height || 200}
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseLeave={stopDrawing}
        style={{
          border: '1px solid #888',
          backgroundColor: '#ffffff',
          width: `${props.width || 200}px`,
          height: `${props.height || 200}px`
        }}
      />
    </div>
  );
});

export default CanvasComponent;