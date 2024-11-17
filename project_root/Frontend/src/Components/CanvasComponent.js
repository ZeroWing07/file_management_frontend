import React, { useRef, useState, useEffect } from 'react';

const CanvasComponent = React.forwardRef((props, ref) => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [context, setContext] = useState(null);

  useEffect(() => {
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');

      // Set up canvas properties
      ctx.lineWidth = 2;
      ctx.lineCap = 'round';
      ctx.strokeStyle = '#000000';

      // Fill the canvas with a white background
      ctx.fillStyle = '#FFFFFF'; // White color
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      setContext(ctx);
    }
  }, []);

  const getMousePos = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    };
  };

  const startDrawing = (e) => {
    const pos = getMousePos(e);
    context.beginPath();
    context.moveTo(pos.x, pos.y);
    setIsDrawing(true);
  };

  const draw = (e) => {
    if (!isDrawing) return;
    const pos = getMousePos(e);
    context.lineTo(pos.x, pos.y);
    context.stroke();
  };

  const stopDrawing = () => {
    context.closePath();
    setIsDrawing(false);
  };

  const clearCanvas = () => {
    context.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
  };

  // Expose canvas ref and clearCanvas method to parent component
  React.useImperativeHandle(ref, () => ({
    toDataURL: () => canvasRef.current.toDataURL(),
    clearCanvas,
  }));

  return (
    <canvas
      ref={canvasRef}
      width={props.width}
      height={props.height}
      onMouseDown={startDrawing}
      onMouseMove={draw}
      onMouseUp={stopDrawing}
      onMouseLeave={stopDrawing}
      style={{ border: '1px solid #888', backgroundColor: '#ffffff' }}
    />
  );
});

export default CanvasComponent;
