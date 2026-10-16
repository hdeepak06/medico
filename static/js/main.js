/**
 * MEDICO - Main JavaScript
 * Handles dynamic interactions, AJAX slot selection, mobile menu, and prescription line items.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Toggle
  const mobileBtn = document.getElementById('mobileMenuToggle');
  const mobileNav = document.getElementById('mobileNav');

  if (mobileBtn && mobileNav) {
    mobileBtn.addEventListener('click', () => {
      const isExpanded = mobileNav.style.display === 'flex';
      mobileNav.style.display = isExpanded ? 'none' : 'flex';
    });
  }

  // 2. Alert Dismissal
  const alertCloseBtns = document.querySelectorAll('.alert-close');
  alertCloseBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        alert.style.transition = 'all 0.25s ease';
        setTimeout(() => alert.remove(), 250);
      }
    });
  });

  // 3. Dynamic Doctor Slot Picker
  const dateInput = document.getElementById('appointmentDateInput');
  const slotContainer = document.getElementById('slotContainer');
  const selectedTimeInput = document.getElementById('selectedTimeInput');
  const doctorSelect = document.getElementById('doctorSelectInput');

  function loadDoctorSlots() {
    if (!slotContainer) return;

    const dateVal = dateInput ? dateInput.value : null;
    const docId = doctorSelect ? doctorSelect.value : (slotContainer.dataset.doctorId || null);

    if (!dateVal || !docId) {
      slotContainer.innerHTML = '<p class="text-muted" style="color: var(--slate-500); font-size: 0.9rem;">Please select an appointment date above to view available consultation slots.</p>';
      return;
    }

    slotContainer.innerHTML = '<div style="padding: 1rem; color: var(--primary); font-weight: 600;"><span class="spinner"></span> Checking doctor calendar & real-time slot availability...</div>';

    fetch(`/api/doctor/${docId}/slots/?date=${dateVal}`)
      .then(res => res.json())
      .then(data => {
        if (data.is_past) {
          slotContainer.innerHTML = '<p style="color: var(--rose); font-size: 0.9rem;">⚠️ Cannot book appointments on past dates. Please pick today or an upcoming date.</p>';
          return;
        }

        if (!data.slots || data.slots.length === 0) {
          slotContainer.innerHTML = '<p style="color: var(--slate-500); font-size: 0.9rem;">No consultation slots configured for this day. Please choose another date.</p>';
          return;
        }

        let html = '<div class="slot-grid">';
        let hasAvailable = false;

        data.slots.forEach(slot => {
          if (slot.is_available) {
            hasAvailable = true;
            html += `<button type="button" class="slot-btn" data-time="${slot.value}">${slot.display}</button>`;
          } else if (slot.is_booked) {
            html += `<button type="button" class="slot-btn booked" disabled title="Already booked by another patient">${slot.display} (Booked)</button>`;
          } else {
            html += `<button type="button" class="slot-btn" disabled title="Slot unavailable">${slot.display}</button>`;
          }
        });
        html += '</div>';

        if (!hasAvailable) {
          html += '<p style="color: var(--amber); font-size: 0.85rem; margin-top: 0.75rem;">All regular slots for this date are fully booked. Please choose an alternate date.</p>';
        }

        slotContainer.innerHTML = html;

        // Attach click listeners to available slot buttons
        const slotButtons = slotContainer.querySelectorAll('.slot-btn:not(:disabled)');
        slotButtons.forEach(btn => {
          btn.addEventListener('click', () => {
            slotButtons.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            if (selectedTimeInput) {
              selectedTimeInput.value = btn.dataset.time;
            }
          });
        });
      })
      .catch(err => {
        console.error('Error fetching slots:', err);
        slotContainer.innerHTML = '<p style="color: var(--rose);">Could not load slots. Please check your connection and try again.</p>';
      });
  }

  if (dateInput) {
    dateInput.addEventListener('change', loadDoctorSlots);
    // If date already pre-filled
    if (dateInput.value) {
      loadDoctorSlots();
    }
  }

  if (doctorSelect) {
    doctorSelect.addEventListener('change', loadDoctorSlots);
  }

  // 4. Dynamic Medicine Items in Doctor Prescription Creator
  const addMedicineBtn = document.getElementById('addMedicineRowBtn');
  const medicineTableBody = document.getElementById('medicineTableBody');

  if (addMedicineBtn && medicineTableBody) {
    addMedicineBtn.addEventListener('click', () => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><input type="text" name="med_name[]" class="form-input" placeholder="e.g. Amoxicillin 500mg" required></td>
        <td><input type="text" name="med_dosage[]" class="form-input" placeholder="1 tablet"></td>
        <td>
          <select name="med_frequency[]" class="form-input">
            <option value="Once daily">Once daily</option>
            <option value="Twice daily" selected>Twice daily</option>
            <option value="Three times daily">Three times daily</option>
            <option value="As needed">As needed (PRN)</option>
          </select>
        </td>
        <td><input type="text" name="med_duration[]" class="form-input" placeholder="7 days"></td>
        <td><input type="text" name="med_instructions[]" class="form-input" placeholder="Take after meals"></td>
        <td style="text-align: center;">
          <button type="button" class="btn btn-sm btn-danger remove-med-btn" style="padding: 0.35rem 0.6rem;">&times;</button>
        </td>
      `;
      medicineTableBody.appendChild(row);

      // Attach remove handler
      row.querySelector('.remove-med-btn').addEventListener('click', () => {
        row.remove();
      });
    });

    // Delegate remove event for initial rows
    medicineTableBody.addEventListener('click', (e) => {
      if (e.target.classList.contains('remove-med-btn')) {
        const tr = e.target.closest('tr');
        if (medicineTableBody.children.length > 1) {
          tr.remove();
        } else {
          alert('Prescription must have at least one medication line.');
        }
      }
    });
  }
});
