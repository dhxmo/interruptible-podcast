import asyncio
import unittest

from AIR.src.deep_research.search import DeepResearcher
from AIR.src.manager import ClientManager
from AIR.src.pod_gen.generate import PodGenStandard
from AIR.src.speech_gen import SpeechGen
from AIR.src.whisper import FasterWhisperEngine
from AIR.tests.constants import podcast_script


class AIRTestCasesUnit(unittest.TestCase):
    def setUp(self):
        self.dr = DeepResearcher()
        self.cm = ClientManager()
        self.session_id = self.cm.create_session()
        self.pg = PodGenStandard()
        self.tts = FasterWhisperEngine()
        self.stt = SpeechGen()
        self.speaker_lookup = {
            "Host1": "am_puck(1)+am_michael(1.5)",
            "Host2": "am_puck(1)+am_echo(1.5)",
        }

    # --- human audio transcribe
    def test_stt(self):
        # TODO: file input for testing. in main, stream audio and save as buffer, pass buffer directly to function
        full_text = self.tts.transcribe(
            self.cm.sessions[self.session_id], "./data/male.wav"
        )

        self.assertGreater(len(full_text), 0)

    # --- deep search based on user query
    def test_web_search_n_scrape(self):
        return asyncio.run(self._web_search_n_scrape())

    async def _web_search_n_scrape(self):
        search_result = await self.dr.web_search_n_scrape(
            self.cm.sessions[self.session_id], "quantum computing"
        )
        self.assertGreater(len(search_result), 0)

    # --- input prompt to talking points
    def test_deep_research_report(self):
        return asyncio.run(self._ds_report())

    async def _ds_report(self):
        user_input = "tell me whats latest in quantum computing"

        talking_points = await self.dr.generate_report(
            user_input, self.cm.sessions[self.session_id]
        )

        self.assertGreater(len(talking_points), 0)

    # --- generate podcast script based on talking points - single. non-chunked
    def test_generate_with_summary_talking_points(self):
        asyncio.run(self._podgen())

    async def _podgen(self):
        talking_points = """
       The field of quantum computing is advancing rapidly across multiple domains, with significant breakthroughs and emerging technologies. Here's an organized overview based on the latest developments:

1. **Exotic Matter Prediction**: Researchers predict new forms of matter, such as non-Abelian anyons, which could be crucial for robust quantum computing. These anyons have unique properties that make them promising for error correction and reliable information processing.

2. **Quantum Sensing and Communication**: Improvements in the accuracy and reliability of quantum states enhance both sensing applications (e.g., detecting changes) and communication technologies (e.g., secure quantum networks).

3. **Topological Quantum Processors**: The development of an eight-qubit topological processor highlights advancements in creating stable qubits, which are less susceptible to environmental noise, thus improving computational reliability.

4. **Hypercube Network Technologies**: These networks address limitations in qubit communication, enhancing the scalability and efficiency of quantum systems by optimizing data transfer between qubits.

5. **Post-Quantum Cryptography**: As quantum computing threatens current encryption methods, this area focuses on developing algorithms resistant to quantum attacks, ensuring secure data transmission in the future.

6. **Quantum Machine Learning Integration**: Frameworks like TorchQC enable machine learning techniques to optimize quantum dynamics and control, potentially enhancing problem-solving efficiency in quantum systems.

7. **Innovative Materials**: Research into materials like germanium-based quantum well lasers aims to improve qubit properties, offering potential advancements in quantum hardware design.

8. **Hybrid Quantum-Classical Systems**: Combining quantum and classical computing leverages the strengths of both, creating systems that can handle tasks more effectively by integrating classical optimization with quantum computation.

9. **Quantum Optimisation Algorithms**: Utilizing Rydberg atom arrays, these algorithms offer improved solutions for complex optimization problems across various industries.

10. **Quantum Chemistry Applications**: Advances in calculating molecular energies could revolutionize fields like drug discovery and materials design, providing insights currently unattainable with classical methods.

In conclusion, quantum computing is evolving across diverse areas, from material science to cryptography and machine learning, promising transformative potential despite challenges. Further exploration of specific technologies and their applications would provide deeper insights into this dynamic field. 
        """

        # self.cm.sessions[self.session_id]["running_summary"]
        running_summary = """
        Recent advancements in quantum computing continue to show promising breakthroughs across multiple fronts. MIT researchers have made significant strides, including:

- **Exotic Matter Prediction**: Physicists at MIT predict a new form of matter that could be crucial for quantum computing. This work suggests the potential creation of non-Abelian anyons without a magnetic field, opening up new avenues for both basic research and future applications.
  
- **Quantum Sensing and Communication**: New theoretical approaches are being developed to generate quantum states with improved accuracy and reliability, enhancing information and decision systems.

- **Superconducting Qubit Fidelity**: Fast control methods have enabled record-setting fidelity in superconducting qubits, promising reduced error-correction resource overhead.

- **Quantum Simulator for Materials Science**: Researchers are using a quantum simulator to explore complex properties of materials by emulating magnetic fields on superconducting quantum computers.

- **Code-Breaking Quantum Computer**: Building on landmark algorithms, researchers propose smaller and more noise-tolerant quantum factoring circuits for cryptography.

- **Exotic Particles Insights**: New insights into excitons from ultrathin materials are being studied through a powerful instrument at the Brookhaven National Laboratory, impacting future electronics.

- **Modular Hardware Architecture**: A new quantum-system-on-chip architecture is enabling efficient control of large arrays of qubits, moving closer to practical quantum computing.

- **Atom Arrangement Techniques**: Physicists have arranged atoms in extremely close proximity, opening possibilities for exploring exotic states of matter and building new quantum materials.

- **Entanglement Structure Tuning**: Advances in tuning the entanglement structure within an array of qubits offer a way to characterize fundamental resources needed for quantum computing.

Additionally, Microsoft has made notable progress:

- **Topological Qubit Demonstration**: They have successfully created the world's first topological qubit, a foundational step towards building fault-tolerant quantum computers.
  
- **Scalability and Future Plans**: Microsoft has already placed eight topological qubits on a chip designed to house one million qubits, indicating their commitment to scalability.

- **DARPA Recognition**: The company received recognition from DARPA's US2QC program for its roadmap towards building fault-tolerant quantum computers using topological qubits.

- **Accelerated Timeline**: Microsoft aims to build a prototype of the machine in years rather than decades, marking significant progress towards practical quantum computing.

These developments highlight the rapid advancement and growing importance of quantum computing technologies.Recent advancements in quantum computing continue to show promising breakthroughs across multiple fronts. MIT researchers have made significant strides, including:

- **Exotic Matter Prediction**: Physicists at MIT predict a new form of matter that could be crucial for quantum computing. This work suggests the potential creation of non-Abelian anyons without a magnetic field, opening up new avenues for both basic research and future applications.

- **Quantum Sensing and Communication**: New theoretical approaches are being developed to generate quantum states with improved accuracy and reliability, enhancing information and decision systems.

- **Superconducting Qubit Fidelity**: Fast control methods have enabled record-setting fidelity in superconducting qubits, promising reduced error-correction resource overhead.

- **Quantum Simulator for Materials Science**: Researchers are using a quantum simulator to explore complex properties of materials by emulating magnetic fields on superconducting quantum computers.

- **Code-Breaking Quantum Computer**: Building on landmark algorithms, researchers propose smaller and more noise-tolerant quantum factoring circuits for cryptography.

- **Exotic Particles Insights**: New insights into excitons from ultrathin materials are being studied through a powerful instrument at the Brookhaven National Laboratory, impacting future electronics.

- **Modular Hardware Architecture**: A new quantum-system-on-chip architecture is enabling efficient control of large arrays of qubits, moving closer to practical quantum computing.

- **Atom Arrangement Techniques**: Physicists have arranged atoms in extremely close proximity, opening possibilities for exploring exotic states of matter and building new quantum materials.

- **Entanglement Structure Tuning**: Advances in tuning the entanglement structure within an array of qubits offer a way to characterize fundamental resources needed for quantum computing.

Additionally, recent developments include:

- **Post-Quantum Cryptography**: Innovations such as hybrid quantum-classical algorithms and novel qubit designs are reducing error rates in quantum circuits. Companies like IBM and Google are investing heavily in research aimed at achieving practical quantum supremacy within the next few years.

- **Machine Learning Integration**: Quantum machine learning integration with tools like TorchQC is advancing artificial intelligence applications, providing unprecedented accuracy in complex problem-solving tasks.

- **Materials Science**: New materials such as germanium and GeSn-based quantum well lasers are under development to improve quantum hardware, promising higher efficiency and better performance for nanoscale devices.

- **Optimization Techniques**: Quantum optimisation techniques, particularly those designed for Rydberg atom arrays, are being explored for complex problems in logistics and energy.

- **Chemistry Applications**: Quantum computing’s application in quantum chemistry has enabled the computation of single-point energies of large molecular systems with unprecedented accuracy, accelerating drug discovery and materials design.

These advancements highlight the significant progress made in various domains such as cryptography, machine learning, materials science, hybrid algorithms, optimisation techniques, and chemical computations. The journey toward quantum supremacy may still have hurdles, but the progress underscores its transformative potential.Based on the provided new search results from various sources, here is an updated summary of the latest developments in quantum computing:

### Latest Developments in Quantum Computing

#### 1. **Topological Quantum Processors**
   - **Breakthrough**: In a significant leap for quantum computing, physicists unveiled an eight-qubit topological quantum processor, marking the first such device.
   - **Implications**: This advancement enhances computational capabilities and paves the way for more robust quantum systems.

#### 2. **Hypercube Network Technologies**
   - **Scalability and Performance**: Hypercube network technologies are being developed to enhance scalability and performance in quantum systems by overcoming traditional limitations in communication between qubits.
   - **Potential**: These networks could enable more robust and efficient quantum computers, addressing one of the key challenges in current quantum hardware.

#### 3. **Post-Quantum Cryptography**
   - **Emerging Threats**: Recent studies emphasize the importance of developing post-quantum cryptographic algorithms to secure sensitive data against potential threats from quantum computing.
   - **References**: Dymova, H. (2024). "Post-quantum cryptography: Addressing emerging threats."

#### 4. **Quantum Machine Learning Integration**
   - **Frameworks and Techniques**: Frameworks like TorchQC are enabling the application of deep learning techniques in quantum dynamics and control.
   - **References**: Koutromanos, D., & Paspalakis, E. (2024). "Quantum machine learning integration with TorchQC."

#### 5. **Innovative Materials**
   - **Germanium and GeSn-Based Quantum Well Lasers**: These materials are being developed to improve quantum hardware, promising higher efficiency and better performance for nanoscale devices.
   - **References**: Joshi, R.S. (2025). "Innovative materials for quantum hardware."

#### 6. **Hybrid Approaches**
   - **Quantum-Classical Systems**: Hybrid approaches are gaining traction by leveraging both quantum and classical systems to exploit the strengths of each while addressing challenging tasks.
   - **References**: Singh, P., & Raman, B. (2025). "Hybrid quantum-classical algorithms."

#### 7. **Quantum Optimisation Algorithms**
   - **Rydberg Atom Arrays**: Quantum optimisation algorithms designed for Rydberg atom arrays are demonstrating significant improvements over classical counterparts in solving complex problems.
   - **References**: Dlaska, C. (2024). "Quantum optimisation techniques and Rydberg atom arrays."

#### 8. **Quantum Chemistry Applications**
   - **Drug Discovery and Materials Design**: Quantum computing is being applied to quantum chemistry, enabling the computation of single-point energies of large molecular systems with unprecedented accuracy.
   - **References**: Barone, V. (2025). "Quantum chemistry applications in drug discovery and materials design."

#### 9. **Practical Implementations**
   - **Artificial Intelligence and System Technologies**: Real-world implementations are expanding, advancing artificial intelligence and enhancing system technologies, making practical innovation and application more evident.
   - **References**: Crilly, P.B. (2024). "Practical implementations of quantum computing."

### Conclusion
The field of quantum computing is rapidly evolving with significant breakthroughs in hardware, algorithms, and practical applications across various domains such as cryptography, machine learning, materials science, hybrid systems, optimisation techniques, and chemical computations. While challenges remain, the progress underscores its transformative potential.

If you need more detailed information or specific references, feel free to ask!
        """

        conversational_tone = "Opinionated - Strong personal takes on topics."

        await self.pg.podgen(
            self.cm.sessions[self.session_id],
            running_summary,
            talking_points,
            conversational_tone,
        )

        self.assertGreater(
            len(self.cm.sessions[self.session_id]["podscript_script"]), 0
        )

    # TODO: --- tts
    def test_tts(self):
        lines = [line.strip() for line in podcast_script.strip().split("\n") if line]
        dialogues = [(line.split(":")[0], line.split(":")[1].strip()) for line in lines]

        for i, (speaker, sentence) in enumerate(dialogues):
            if speaker not in self.speaker_lookup:
                continue

            self.stt.stream_response(None, self.speaker_lookup[speaker], sentence)

    # TODO: --- split on sentences and implement human interrupt
    def test_queue_fetch_interrupt_contextual_update_in_queue(self):
        # simulate interrupt with a keydown and implement logic
        pass

    # --- TODO: total --> do this with the UI. NOT HERE.
    def test_stream_podcast_script_2_tts_2_client(self):
        pass

    def test_process_interruption_and_stream_contextual_response_back(self):
        # use running summary + embed for session vector db to respond and continue convo
        pass


if __name__ == "__main__":
    unittest.main()
