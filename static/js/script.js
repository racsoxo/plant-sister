console.log('Script cargado correctamente');

// Variables globales
let plantaIdentificada = null;
let fotoCapturada = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM cargado');
    
    const btnAbrirModal = document.getElementById('btnAbrirModal');
    const modal = document.getElementById('modal-nueva-planta');
    const nombreBusqueda = document.getElementById('nombre-busqueda');
    const btnGuardar = document.getElementById('btnGuardar');
    const btnVolver = document.getElementById('btnVolver');
    
    console.log('Botón:', btnAbrirModal);
    console.log('Modal:', modal);

    const btnCerrar = document.getElementById('btnCerrar');
    const btnSubirFoto = document.getElementById('btnSubirFoto');
    const btnTomarFoto = document.getElementById('btnTomarFoto');
    const imagenInput = document.getElementById('imagen-input');
    const btnCancelar = document.getElementById('btnCancelar');

    // Event Listeners principales
    if (btnAbrirModal) {
        btnAbrirModal.addEventListener('click', () => {
            console.log('Botón clickeado');
            if (modal) {
                modal.classList.add('visible');
                document.body.style.overflow = 'hidden';
            }
        });
    }

    if (btnCerrar) {
        btnCerrar.addEventListener('click', cerrarModal);
    }

    if (btnCancelar) {
        btnCancelar.addEventListener('click', cerrarModal);
    }

    if (btnSubirFoto) {
        btnSubirFoto.addEventListener('click', () => imagenInput.click());
    }

    if (imagenInput) {
        imagenInput.addEventListener('change', async (event) => {
            const file = event.target.files[0];
            if (!file) return;

            try {
                const formData = new FormData();
                formData.append('imagen', file);

                const infoDiv = document.getElementById('info-identificacion');
                if (infoDiv) {
                    infoDiv.innerHTML = '<div class="loading">Identificando planta...</div>';
                }

                // Mostrar preview de la imagen
                const previewImagen = document.getElementById('preview-imagen');
                if (previewImagen) {
                    previewImagen.src = URL.createObjectURL(file);
                    previewImagen.style.display = 'block';
                }

                // Cambiar a paso 2
                document.getElementById('paso-1').style.display = 'none';
                document.getElementById('paso-2').style.display = 'block';

                const response = await fetch('/procesar_imagen', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                mostrarResultadoIdentificacion(data);

            } catch (error) {
                console.error('Error:', error);
                mostrarMensaje('Error al procesar la imagen', 'error');
            }
        });
    }

    // Cerrar modal con Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') cerrarModal();
    });

    // Cerrar modal al hacer clic fuera
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) cerrarModal();
        });
    }

    // Búsqueda por nombre
    if (nombreBusqueda) {
        nombreBusqueda.addEventListener('input', debounce(async (e) => {
            const busqueda = e.target.value.trim();
            const resultadosContainer = document.getElementById('resultados-busqueda');
            
            if (busqueda.length < 3) {
                resultadosContainer.style.display = 'none';
                return;
            }

            try {
                const response = await fetch(`/buscar_planta?nombre=${encodeURIComponent(busqueda)}`);
                const data = await response.json();
                
                if (response.status === 404) {
                    resultadosContainer.innerHTML = `
                        <div class="resultado-busqueda error">
                            <p>No se encontró ninguna planta con ese nombre.</p>
                            <p>Intenta con otro nombre o usa una foto para identificarla.</p>
                        </div>`;
                    resultadosContainer.style.display = 'block';
                    return;
                }
                
                if (!response.ok) {
                    throw new Error(data.error || 'Error en la búsqueda');
                }
                
                mostrarResultadosBusqueda(data);
                
            } catch (error) {
                console.error('Error:', error);
                resultadosContainer.innerHTML = `
                    <div class="resultado-busqueda error">
                        <p>Error al buscar la planta.</p>
                        <p>Por favor, intenta nuevamente.</p>
                    </div>`;
                resultadosContainer.style.display = 'block';
            }
        }, 300));
    }

    // Guardar planta
    if (btnGuardar) {
        btnGuardar.addEventListener('click', async () => {
            if (!plantaIdentificada) {
                mostrarMensaje('Por favor, identifica primero la planta', 'error');
                return;
            }

            const aliasInput = document.getElementById('alias-planta');
            const datosPlanta = {
                ...plantaIdentificada
            };

            if (aliasInput && aliasInput.value.trim()) {
                datosPlanta.alias = aliasInput.value.trim();
            }

            try {
                const response = await fetch('/guardar_planta', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(datosPlanta)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Error al guardar la planta');
                }

                const data = await response.json();
                mostrarMensaje('Planta guardada con éxito', 'success');
                setTimeout(() => window.location.reload(), 1500);

            } catch (error) {
                console.error('Error:', error);
                mostrarMensaje(error.message || 'Error al guardar la planta', 'error');
            }
        });
    }

    // Volver al paso 1
    if (btnVolver) {
        btnVolver.addEventListener('click', () => {
            document.getElementById('paso-1').style.display = 'block';
            document.getElementById('paso-2').style.display = 'none';
            resetearFormulario();
        });
    }
});

// Función debounce para evitar muchas peticiones
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Funciones principales
function cerrarModal() {
    const modal = document.getElementById('modal-nueva-planta');
    if (modal) {
        modal.classList.remove('visible');
        document.body.style.overflow = 'auto';
        resetearFormulario();
    }
}

function resetearFormulario() {
    const previewContainer = document.getElementById('preview-container');
    const imagenInput = document.getElementById('imagen-input');
    const aliasInput = document.getElementById('alias-planta');

    if (previewContainer) previewContainer.style.display = 'none';
    if (imagenInput) imagenInput.value = '';
    if (aliasInput) aliasInput.value = '';
}

async function buscarPorNombre(nombre) {
    try {
        console.log('Buscando:', nombre);
        const resultadosDiv = document.getElementById('resultados-busqueda');
        
        if (resultadosDiv) {
            resultadosDiv.style.display = 'block';
            resultadosDiv.innerHTML = '<div class="buscando">Buscando...</div>';
        }

        const response = await fetch('/buscar_planta', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ nombre: nombre })
        });

        const data = await response.json();
        
        if (data.error) {
            resultadosDiv.innerHTML = '<div class="resultado-item">No se encontraron resultados</div>';
            return;
        }

        // Mostrar el resultado
        resultadosDiv.innerHTML = `
            <div class="resultado-item" onclick="seleccionarPlanta(${JSON.stringify(data).replace(/"/g, '&quot;')})">
                <h4>${data.nombre_comun}</h4>
                <p>${data.nombre_cientifico}</p>
            </div>
        `;

    } catch (error) {
        console.error('Error:', error);
        const resultadosDiv = document.getElementById('resultados-busqueda');
        if (resultadosDiv) {
            resultadosDiv.innerHTML = '<div class="resultado-item">Error al buscar la planta</div>';
        }
    }
}

function seleccionarPlanta(planta) {
    try {
        // Si planta es string (por el JSON.stringify), parsearlo
        if (typeof planta === 'string') {
            planta = JSON.parse(planta);
        }

        document.getElementById('paso-1').style.display = 'none';
        document.getElementById('paso-2').style.display = 'block';
        
        const infoDiv = document.getElementById('info-identificacion');
        if (infoDiv) {
            infoDiv.innerHTML = `
                <div class="info-planta">
                    <h3>${planta.nombre_comun}</h3>
                    <p class="nombre-cientifico">${planta.nombre_cientifico}</p>
                    <p class="detalles">Riego: ${planta.frecuencia_riego}</p>
                </div>
            `;
        }
        
        plantaIdentificada = planta;
    } catch (error) {
        console.error('Error al seleccionar planta:', error);
        mostrarMensaje('Error al seleccionar la planta', 'error');
    }
}

function volverPaso1() {
    console.log('Volviendo al paso 1');
    document.getElementById('paso-2').style.display = 'none';
    document.getElementById('paso-1').style.display = 'block';
    
    // Limpiar campos
    const searchInput = document.getElementById('nombre-busqueda');
    if (searchInput) {
        searchInput.value = '';
    }
    const aliasInput = document.getElementById('alias-planta');
    if (aliasInput) {
        aliasInput.value = '';
    }
}

async function guardarPlanta() {
    console.log('Guardando planta...');
    const aliasInput = document.getElementById('alias-planta');
    const alias = aliasInput ? aliasInput.value.trim() : '';
    
    if (!alias) {
        mostrarMensaje('Por favor, dale un nombre a tu planta', 'error');
        return;
    }

    if (!plantaIdentificada) {
        mostrarMensaje('Error: No hay planta seleccionada', 'error');
        return;
    }

    try {
        const datos = {
            nombre_comun: plantaIdentificada.nombre_comun,
            nombre_cientifico: plantaIdentificada.nombre_cientifico,
            frecuencia_riego: plantaIdentificada.frecuencia_riego,
            alias: alias
        };

        console.log('Enviando datos:', datos);
        const response = await fetch('/guardar_planta', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(datos)
        });

        const result = await response.json();

        if (result.error) {
            throw new Error(result.error);
        }

        mostrarMensaje('¡Planta guardada con éxito!', 'success');
        
        // Esperar un momento antes de cerrar para que se vea el mensaje
        setTimeout(() => {
            cerrarFormulario();
        }, 1500);

    } catch (error) {
        console.error('Error al guardar:', error);
        mostrarMensaje('Error al guardar la planta', 'error');
    }
}

function mostrarMensaje(mensaje, tipo = 'info') {
    const mensajeDiv = document.createElement('div');
    mensajeDiv.className = `mensaje-flotante mensaje-${tipo}`;
    mensajeDiv.textContent = mensaje;
    
    document.body.appendChild(mensajeDiv);
    
    setTimeout(() => {
        mensajeDiv.classList.add('mensaje-saliendo');
        setTimeout(() => mensajeDiv.remove(), 300);
    }, 3000);
}

// Agregar estilos para los mensajes flotantes
const style = document.createElement('style');
style.textContent = `
    .mensaje-flotante {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        padding: 12px 24px;
        border-radius: 8px;
        background: #333;
        color: white;
        z-index: 1000;
        animation: slideUp 0.3s ease;
    }

    .mensaje-flotante.mensaje-error {
        background: #f44336;
    }

    .mensaje-flotante.mensaje-success {
        background: #4caf50;
    }

    .mensaje-saliendo {
        animation: slideDown 0.3s ease;
    }

    @keyframes slideUp {
        from { transform: translate(-50%, 100%); opacity: 0; }
        to { transform: translate(-50%, 0); opacity: 1; }
    }

    @keyframes slideDown {
        from { transform: translate(-50%, 0); opacity: 1; }
        to { transform: translate(-50%, 100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

function mostrarResultadosBusqueda(resultados) {
    const container = document.getElementById('resultados-busqueda');
    if (!container) return;

    container.innerHTML = resultados.map(planta => `
        <div class="resultado-busqueda" onclick="seleccionarPlantaPorNombre(${JSON.stringify(planta).replace(/'/g, "&#39;")})">
            <h4>${planta.nombre_comun}</h4>
            <p class="nombre-cientifico">${planta.nombre_cientifico}</p>
            <p class="riego-info">${planta.frecuencia_riego}</p>
        </div>
    `).join('');

    container.style.display = 'block';
}

function seleccionarPlantaPorNombre(planta) {
    plantaIdentificada = planta;
    
    // Mostrar la información pero mantener visible el paso 1
    const infoDiv = document.getElementById('info-identificacion');
    if (infoDiv) {
        infoDiv.innerHTML = `
            <div class="planta-identificada">
                <div class="info">
                    <h3>${planta.nombre_comun}</h3>
                    <p class="nombre-cientifico">${planta.nombre_cientifico}</p>
                    <p>Riego: ${planta.frecuencia_riego}</p>
                </div>
            </div>
        `;
    }
    
    // Mostrar el paso 2 sin ocultar el paso 1
    document.getElementById('paso-2').style.display = 'block';
}

async function procesarImagenCargada(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Mostrar mensaje de "Identificando planta..."
    const infoDiv = document.getElementById('info-identificacion');
    if (infoDiv) {
        infoDiv.innerHTML = `
            <div class="identificando-mensaje">
                <div class="spinner"></div>
                <p>Identificando planta...</p>
            </div>
        `;
    }

    try {
        const formData = new FormData();
        formData.append('imagen', file);

        // Si ya tenemos una planta identificada por nombre, solo guardamos la imagen
        if (plantaIdentificada) {
            const response = await fetch('/guardar_imagen', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Error al guardar la imagen');
            
            const data = await response.json();
            plantaIdentificada.imagen = data.filename;

            // Actualizar la visualización con la imagen
            actualizarVisualizacionConImagen(data.filename);
        } else {
            // Si no hay planta identificada, intentamos identificar por imagen
            const response = await fetch('/procesar_imagen', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (!response.ok || data.error) {
                throw new Error(data.error || 'No se pudo identificar la planta');
            }

            plantaIdentificada = data;
            mostrarInformacionPlanta(data);
        }

        document.getElementById('paso-2').style.display = 'block';
        
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje(error.message, 'error');
        // Limpiar el mensaje de identificación
        if (infoDiv) {
            infoDiv.innerHTML = '';
        }
    }
}

function actualizarVisualizacionConImagen(filename) {
    const infoDiv = document.querySelector('.planta-identificada');
    if (infoDiv) {
        // Si ya existe una imagen, la reemplazamos
        let imagen = infoDiv.querySelector('img');
        if (imagen) {
            imagen.src = `/static/uploads/${filename}`;
        } else {
            // Si no existe la imagen, la agregamos
            const imagenHTML = `<img src="/static/uploads/${filename}" alt="Imagen de planta">`;
            infoDiv.insertAdjacentHTML('afterbegin', imagenHTML);
        }
    }
}

function mostrarResultadoIdentificacion(data) {
    const infoDiv = document.getElementById('info-identificacion');
    if (!infoDiv) return;

    infoDiv.innerHTML = `
        <div class="info-planta">
            <h3>${data.nombre_comun}</h3>
            <p class="nombre-cientifico">${data.nombre_cientifico}</p>
            <p class="detalles">Riego: ${data.frecuencia_riego}</p>
            ${data.summary ? `<p class="wiki-info">${data.summary}</p>` : ''}
        </div>
    `;
}

// Actualizar el botón de cerrar modal
document.getElementById('btnCerrarModal').addEventListener('click', () => {
    const modal = document.getElementById('modal-nueva-planta');
    modal.style.display = 'none';
    // Limpiar el estado
    plantaIdentificada = null;
    document.getElementById('nombre-busqueda').value = '';
    document.getElementById('alias-planta').value = '';
    document.getElementById('info-identificacion').innerHTML = '';
    document.getElementById('paso-2').style.display = 'none';
    document.getElementById('resultados-busqueda').style.display = 'none';
});

// Actualizar el guardado
document.getElementById('btnGuardar').addEventListener('click', async () => {
    if (!plantaIdentificada) {
        mostrarMensaje('Por favor, identifica primero la planta', 'error');
        return;
    }

    const aliasInput = document.getElementById('alias-planta');
    const datosPlanta = {
        ...plantaIdentificada,
        alias: aliasInput.value.trim() || plantaIdentificada.nombre_comun
    };

    try {
        const response = await fetch('/guardar_planta', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(datosPlanta)
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Error al guardar');
        }

        mostrarMensaje('Planta guardada con éxito', 'success');
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    } catch (error) {
        console.error('Error:', error);
        mostrarMensaje(error.message, 'error');
    }
});
