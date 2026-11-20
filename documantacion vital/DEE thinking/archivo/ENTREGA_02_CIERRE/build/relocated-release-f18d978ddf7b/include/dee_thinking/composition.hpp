#pragma once

#include "dee_thinking/organization_catalog.hpp"

#include <cstdint>
#include <map>
#include <string>
#include <vector>

namespace dee::thinking::catalog {

enum class DiagnosticSeverity : std::uint8_t { Information = 1, Warning = 2, Error = 3 };
enum class VerificationClass : std::uint8_t {
    StaticVerified = 1,
    RequiresSimulation = 2,
    Unsupported = 3,
};

struct Diagnostic {
    DiagnosticSeverity severity{DiagnosticSeverity::Information};
    VerificationClass verification{VerificationClass::StaticVerified};
    std::string code;
    std::string message;
};

struct Endpoint {
    std::string instance;
    std::string port;
};

struct ConnectionRequest {
    Endpoint source;
    Endpoint target;
    std::string purpose;
};

struct ConnectionRecord {
    ConnectionRequest request;
    VerificationClass verification{VerificationClass::RequiresSimulation};
    std::string physical_contract;
};

struct PortInputRequest {
    std::string instance;
    std::string port;
    std::uint16_t s_reg{};
};

class ComposedWorld {
public:
    // Reconstructs the composition recipe carried by a Runtime snapshot v2,
    // verifies it against the selected catalog, and then installs the saved
    // Runtime state.  The one-argument overload uses the built-in catalog.
    [[nodiscard]] static ComposedWorld load_snapshot(const std::string& path);
    [[nodiscard]] static ComposedWorld load_snapshot(const std::string& path,
                                                     const OrganizationCatalog& catalog);

    [[nodiscard]] Runtime& runtime() noexcept { return runtime_; }
    [[nodiscard]] const Runtime& runtime() const noexcept { return runtime_; }
    [[nodiscard]] const std::vector<OrganizationInstance>& organizations() const noexcept { return organizations_; }
    [[nodiscard]] const std::vector<ConnectionRecord>& connections() const noexcept { return connections_; }
    [[nodiscard]] const std::map<std::string, Coordinate>& landmarks() const noexcept { return landmarks_; }
    [[nodiscard]] std::string qualified_channel(const std::string& instance, const std::string& local_name) const;
    EventReceipt experience(const std::string& instance, const std::string& port,
                            std::uint64_t at_tick, std::uint16_t s_reg);
    EventReceipt experience_batch(const std::vector<PortInputRequest>& inputs,
                                  std::uint64_t at_tick);
    EventReceipt probe(const std::string& instance, const std::string& port,
                       std::uint64_t at_tick, std::uint16_t s_reg);
    // Stable composition identity. Runtime state such as tick, RAW, queues and
    // backend selection belongs to the snapshot payload, not to this manifest.
    [[nodiscard]] std::string manifest_json() const;
    void save_manifest(const std::string& path) const;
    void save_snapshot(const std::string& path) const;
    void restore_snapshot(const std::string& path);

private:
    ComposedWorld(Runtime runtime,
                  std::vector<OrganizationInstance> organizations,
                  std::vector<ConnectionRecord> connections,
                  std::map<std::string, Coordinate> landmarks);

    Runtime runtime_;
    std::vector<OrganizationInstance> organizations_;
    std::vector<ConnectionRecord> connections_;
    std::map<std::string, Coordinate> landmarks_;

    friend class CompositionPlanner;
};

class CompositionPlanner {
public:
    explicit CompositionPlanner(int dimension);

    void add(OrganizationInstance organization);
    void connect(ConnectionRequest connection);

    [[nodiscard]] int dimension() const noexcept { return dimension_; }
    [[nodiscard]] const std::vector<OrganizationInstance>& organizations() const noexcept { return organizations_; }
    [[nodiscard]] const std::vector<ConnectionRequest>& requested_connections() const noexcept { return connections_; }
    [[nodiscard]] std::vector<Diagnostic> analyze() const;
    [[nodiscard]] ComposedWorld build() const;

private:
    [[nodiscard]] const OrganizationInstance* find_instance(const std::string& id) const noexcept;
    int dimension_{};
    std::vector<OrganizationInstance> organizations_;
    std::vector<ConnectionRequest> connections_;
};

[[nodiscard]] const char* to_string(DiagnosticSeverity value) noexcept;
[[nodiscard]] const char* to_string(VerificationClass value) noexcept;

}  // namespace dee::thinking::catalog
