const io = require("socket.io")(3500, {
  cors: { origin: "*" },
});

io.on("connection", (socket) => {
  console.log(`🔗 User connected: ${socket.id}`);

  socket.on("sdp", (data) => {
    console.log(`📡 Forwarding SDP: ${data.type}`);
    socket.broadcast.emit("sdp", data);
  });

  socket.on("ICEcandidate", (data) => {
    console.log(`🌍 Forwarding ICE Candidate:\n${JSON.stringify(data)}`);
    socket.broadcast.emit("ICEcandidate", data);
  });

  socket.on("disconnect", () => {
    console.log(`❌ User disconnected: ${socket.id}`);
  });
});
